from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.utils import platform

class AppState:
    monitoring_active = False
    active_limits = {}

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        
        layout = FloatLayout()
        
        with layout.canvas.before:
            Color(0.08, 0.09, 0.12, 1)
            self.bg = Rectangle(pos=(0, 0), size=(1000, 1000))
        layout.bind(pos=self.update_bg, size=self.update_bg)

        title = Label(
            text='[b]Edge Light Focus[/b]',
            markup=True,
            font_size=28,
            size_hint=(None, None),
            size=(300, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.88},
            color=(0.9, 0.9, 0.9, 1)
        )
        layout.add_widget(title)

        subtitle = Label(
            text='Manage your app usage and stay focused',
            font_size=14,
            size_hint=(None, None),
            size=(300, 30),
            pos_hint={'center_x': 0.5, 'center_y': 0.82},
            color=(0.6, 0.6, 0.6, 1)
        )
        layout.add_widget(subtitle)

        self.config_btn = Button(
            text='Select Apps & Set Limits',
            size_hint=(None, None),
            size=(260, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.65},
            background_normal='',
            background_color=(0.15, 0.5, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size=16,
            bold=True
        )
        self.config_btn.bind(on_press=self.goto_config)
        layout.add_widget(self.config_btn)

        self.settings_btn = Button(
            text='Open Usage Access Settings',
            size_hint=(None, None),
            size=(260, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            background_normal='',
            background_color=(0.2, 0.25, 0.32, 1),
            color=(1, 1, 1, 1),
            font_size=15
        )
        self.settings_btn.bind(on_press=self.open_usage_settings)
        layout.add_widget(self.settings_btn)

        self.stop_btn = Button(
            text='Stop Monitoring',
            size_hint=(None, None),
            size=(260, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.39},
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=15,
            bold=True
        )
        self.stop_btn.bind(on_press=self.stop_monitoring)
        layout.add_widget(self.stop_btn)

        self.status_lbl = Label(
            text='Status: Monitoring Inactive',
            font_size=14,
            size_hint=(None, None),
            size=(300, 40),
            pos_hint={'center_x': 0.5, 'center_y': 0.22},
            color=(0.3, 0.8, 0.4, 1)
        )
        layout.add_widget(self.status_lbl)

        self.add_widget(layout)

    def on_enter(self, *args):
        if AppState.monitoring_active:
            self.status_lbl.text = 'Status: Monitoring Active'
            self.status_lbl.color = (0.2, 0.8, 0.3, 1)
        else:
            self.status_lbl.text = 'Status: Monitoring Inactive'
            self.status_lbl.color = (0.9, 0.4, 0.3, 1)

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def goto_config(self, instance):
        self.manager.current = 'config'

    def stop_monitoring(self, instance):
        AppState.monitoring_active = False
        AppState.active_limits = {}
        self.status_lbl.text = 'Status: Monitoring Stopped'
        self.status_lbl.color = (0.9, 0.4, 0.3, 1)
        print("Monitoring stopped and reset.")

    def open_usage_settings(self, instance):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                activity = PythonActivity.mActivity
                intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
                activity.startActivity(intent)
            except Exception as e:
                print(f"Error opening usage settings: {e}")
        else:
            print("Usage settings can only be opened on an Android device (PC Test Mode).")


class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)
        
        layout = FloatLayout()
        
        with layout.canvas.before:
            Color(0.08, 0.09, 0.12, 1)
            self.bg = Rectangle(pos=(0, 0), size=(1000, 1000))
        layout.bind(pos=self.update_bg, size=self.update_bg)

        title = Label(
            text='[b]Configure App Limits[/b]',
            markup=True,
            font_size=24,
            size_hint=(None, None),
            size=(300, 40),
            pos_hint={'center_x': 0.5, 'center_y': 0.92},
            color=(0.9, 0.9, 0.9, 1)
        )
        layout.add_widget(title)

        instruction_lbl = Label(
            text='Toggle apps ON/OFF and set limit in Minutes:',
            font_size=13,
            size_hint=(None, None),
            size=(380, 30),
            pos_hint={'center_x': 0.5, 'center_y': 0.84},
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(instruction_lbl)

        scroll = ScrollView(
            size_hint=(None, None),
            size=(400, 330),
            pos_hint={'center_x': 0.5, 'center_y': 0.52}
        )
        
        self.app_list_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15,
            padding=10
        )
        self.app_list_layout.bind(minimum_height=self.app_list_layout.setter('height'))

        self.app_inputs = {}
        installed_apps = self.get_installed_apps()

        for app_name, pkg in installed_apps:
            # Added a larger spacing between elements inside the row
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=20)
            
            # Switch toggle on the left side with explicit size
            switch = Switch(active=False, size_hint_x=None, width=70, pos_hint={'center_y': 0.5})
            
            # App Name label with padding and clear space from switch
            lbl = Label(
                text=app_name,
                color=(0.9, 0.9, 0.9, 1),
                font_size=15,
                bold=True,
                halign='left',
                valign='middle',
                size_hint_x=1,
                pos_hint={'center_y': 0.5}
            )
            lbl.bind(size=lbl.setter('text_size'))
            
            # TextInput for minutes limit on the right side
            txt = TextInput(
                text='5',
                multiline=False,
                size_hint_x=None,
                width=75,
                height=42,
                size_hint_y=None,
                pos_hint={'center_y': 0.5},
                font_size=15,
                halign='center'
            )
            
            row.add_widget(switch)
            row.add_widget(lbl)
            row.add_widget(txt)
            
            self.app_list_layout.add_widget(row)
            self.app_inputs[pkg] = (switch, txt)

        scroll.add_widget(self.app_list_layout)
        layout.add_widget(scroll)

        self.save_btn = Button(
            text='Save & Start Monitoring',
            size_hint=(None, None),
            size=(260, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.16},
            background_normal='',
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=15
        )
        self.save_btn.bind(on_press=self.save_and_start)
        layout.add_widget(self.save_btn)

        self.back_btn = Button(
            text='Back',
            size_hint=(None, None),
            size=(120, 40),
            pos_hint={'center_x': 0.5, 'center_y': 0.08},
            background_normal='',
            background_color=(0.3, 0.3, 0.35, 1),
            color=(1, 1, 1, 1),
            font_size=14
        )
        self.back_btn.bind(on_press=self.go_back)
        layout.add_widget(self.back_btn)

        self.add_widget(layout)

    def get_installed_apps(self):
        apps = []
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                pm = activity.getPackageManager()
                intent = autoclass('android.content.Intent')(autoclass('android.content.Intent.ACTION_MAIN'), None)
                intent.addCategory(autoclass('android.content.Intent.CATEGORY_LAUNCHER'))
                resolve_infos = pm.queryIntentActivities(intent, 0)
                
                for info in resolve_infos:
                    pkg = info.activityInfo.packageName
                    label = info.loadLabel(pm).toString()
                    apps.append((label, pkg))
            except Exception as e:
                print(f"Error fetching installed apps: {e}")
        
        if not apps:
            apps = [
                ("Instagram", "com.instagram.android"),
                ("TikTok", "com.zhiliaoapp.musically"),
                ("YouTube", "com.google.android.youtube"),
                ("Facebook", "com.facebook.katana"),
                ("WhatsApp", "com.whatsapp")
            ]
        return apps

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def save_and_start(self, instance):
        selected_limits = {}
        for pkg, (switch, txt) in self.app_inputs.items():
            if switch.active:
                try:
                    minutes = float(txt.text)
                    selected_limits[pkg] = minutes * 60
                except ValueError:
                    selected_limits[pkg] = 300.0
        
        AppState.active_limits = selected_limits
        AppState.monitoring_active = True
        print(f"Monitoring started with limits (seconds): {AppState.active_limits}")
        self.manager.current = 'dashboard'

    def go_back(self, instance):
        self.manager.current = 'dashboard'


class EdgeLightApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ConfigScreen(name='config'))
        return sm

if __name__ == '__main__':
    EdgeLightApp().run()