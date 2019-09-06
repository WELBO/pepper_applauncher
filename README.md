# Pepper AppLauncher

This is a simple service that loads a config file which contains the apps that you want pepper to display when no app is running, for example on boot.

You only have to change the contents of this config file.

The config file name is `config/app_config.json`

Example content is:
```
{
  "title": "Select an App",
  "apps":[
    {
      "title": "WELBO App",
      "app_id": "welbo_cloud/behavior_1",
      "app_logo": "cloud.png",
      "default": false
    },
    {
      "title": "Dance",
      "app_id": "arcadia/full_launcher",
      "app_logo": "ballet.png"
    },
    {
      "title": "Settings",
      "app_id": "boot-config/.",
      "app_logo": "settings.png"
    }
  ]
}
```

The `title` property corresponds to the name of the app on Pepper's tablet.
The `app_logo` is the image that is displayed on the app launcher. You can select any of the images that are currently present in the `html\resources` folder or add your own images there.
The `app_id` property corresponds to the behaviour you want to start
The optional `default` property can be set to `true` on **ONE** app. When it is set the
applauncher will start this app after a 10 seconds timeout, if no choice has been made
by the user.

