import pyudev

context = pyudev.Context()
devices = context.list_devices(subsystem='input', ID_BUS='usb')

for device in devices:
        props = device.properties
        if 'ID_SERIAL_SHORT' in props:
            print(props['ID_SERIAL_SHORT'])
        else:
            print(props) 
            
