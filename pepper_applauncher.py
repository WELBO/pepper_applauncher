#!/usr/bin/env python
import qi
import sys
import json
import os
import time


class PepperAppLauncher:
    services_connected = None

    def __init__(self, application):
        # Getting a session that will be reused everywhere
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        # Getting a logger. Logs will be in /var/log/naoqi/servicemanager/{application id}.{service name}
        self.logger = qi.Logger(self.service_name)

        # Do some initializations before the service is registered to NAOqi
        self.logger.info("Initializing...")
        self.connect_services()

        self.logger.info("Initialized!")

    def mycallback(self, value):
        print "val:", value

    @qi.nobind
    def start_service(self):
        self.logger.info("Starting service...")

        self.loadAppNames()
        self.loadSettingAutoUpdate()
        self.show_local('index.html')

        self.logger.info("Started!")
        print("started service")

        self.memory = self.session.service('ALMemory')
        self.tabletService = self.session.service("ALTabletService")
        self.ALStore = self.session.service('ALStore')


        self.memory.insertData("WelboAPPL/apps_updated", True )
        self.memory.insertData("WelboAPPL/checked_store", False )


        autoUpdate = self.memory.getData("WelboAPPL/auto_update")
        wifiStatus = self.tabletService.getWifiStatus()
        appsStatus = self.ALStore.status()

        self.memory.insertData("WelboAPPL/checked_store", True )

        #The next two lines are handy for debugging
        # for app in appsStatus:
           # print (str(app['status']) + " "+ str(app['uuid']))

        self.logger.info(autoUpdate + "  " + wifiStatus)
        if (any(app.get('status', None) != 1 for app in appsStatus) and autoUpdate == "True" and wifiStatus == "CONNECTED"):
            print "Found an update, will update the apps!"
            self.memory.insertData("WelboAPPL/apps_updated", False )
            self.ALStore.update()

        self.memory.insertData("WelboAPPL/apps_updated", True )

        print("Evertyhing should now be up to date")

    @qi.nobind
    def stop_service(self):
        # probably useless, unless one method needs to stop the service from inside.
        # external naoqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.application.stop()
        self.logger.info("Stopped!")

    @qi.nobind
    def connect_services(self):
        # connect all services required by your module
        # done in async way over 30s,
        # so it works even if other services are not yet ready when you start your module
        # this is required when the service is autorun as it may start before other modules...
        self.logger.info('Connecting services...')
        self.services_connected = qi.Promise()
        services_connected_fut = self.services_connected.future()

        def get_services():
            try:
                self.memory = self.session.service('ALMemory')
                self.ts = self.session.service("ALTabletService")

                self.logger.info('All services are now connected')
                self.services_connected.setValue(True)
            except RuntimeError as e:
                self.logger.warning('Still missing some service:\n {}'.format(e))

        get_services_task = qi.PeriodicTask()
        get_services_task.setCallback(get_services)
        get_services_task.setUsPeriod(int(2*1000000))  # check every 2s
        get_services_task.start(True)
        try:
            services_connected_fut.value(30*1000)  # timeout = 30s
            get_services_task.stop()
        except RuntimeError:
            get_services_task.stop()
            self.logger.error('Failed to reach all services after 30 seconds')
            raise RuntimeError


    ### Utility functions ###
    def loadAppNames(self):
        # open file
        path = "config/app_config.json"

        try:
            with open(path) as data_file:
                data = json.load(data_file)
                self.memory.insertData("WelboAPPL/app_data", json.dumps(data) )

        except:
            path = "config/error.json"
            with open(path) as data_file:
                data = json.load(data_file)
                self.memory.insertData("WelboAPPL/app_data", json.dumps(data) )

    def loadSettingAutoUpdate(self):
        preferenceManager = self.session.service("ALPreferenceManager")
        autoUpdate = str(preferenceManager.getValue("com.welbo.config","autoUpdate"))
        self.memory.insertData("WelboAPPL/auto_update", autoUpdate )

    def show_local(self,page):
        self.show('http://198.18.0.1/apps/pepper-app-launcher-service/'+page)

    def show(self,page):
        print("Showing a new page")
        self.ts.showWebview(page)

    ### ################# ###

    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")
        # do something
        self.logger.info("End!")

if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python my_super_service.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = PepperAppLauncher(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_service()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)

    #service_instance.show_local('index.html')
