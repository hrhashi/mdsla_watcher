from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv

import sys
import time
import threading
from email.mime.text import MIMEText
from sendmail import MailClient

# Watcher function
def watcher(mc, msg):
    while True:
        time.sleep(1)
        print("Watching MultiDSLA staus. [{0}]".format(time.time() - lastTrapAt))

        if time.time() - lastTrapAt >= TIMEOUT:
            mc.reconnect()
            mc.login_auto()
            mc.sendmail(msg)
            mc.quit()
            
            while True:
                print("MultiDSLA not responding!! [{0}]".format(time.time() - lastTrapAt))
                time.sleep(1)
                
                if time.time() - lastTrapAt < TIMEOUT:
                    print("MultiDSLA has recovered.")
                    break


# Callback function for receiving notifications
# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    #print('Notification from ContextEngineId {0}, ContextName {1}'.format(contextEngineId, contextName))
    for name, val in varBinds:
        print('{0} = {1}'.format(name, val))   
        # if Heart Beat received, reset timer
        if str(name) == "1.3.6.1.6.3.1.1.4.1.0" and str(val) == "1.3.6.1.4.1.24888.1.2.2.14":
            global lastTrapAt
            lastTrapAt = time.time()



if __name__ == '__main__':

    # Mail client
    # Please change mail address
    mail_addr = '******.******@gmail.com'
    mc = MailClient(mail_addr, 'smtp.gmail.com')
    
    # Check connection, then login to Mail Server
    if mc.isConnectionFailed():
        sys.exit(None)
    if not mc.login():
        sys.exit(None)
    mc.quit()

    # Mail message
    msg = MIMEText('Please check status of MultiDSLA and restart it if needed.')
    msg['Subject'] = 'MultiDSLA not responding!!'
    msg['From'] = mail_addr
    msg['To'] = mail_addr


    # Create SNMP engine with autogenernated engineID and pre-bound
    # to socket transport dispatcher
    snmpEngine = engine.SnmpEngine()

    # Transport setup
    # UDP over IPv4, first listening interface/port
    config.addTransport(
        snmpEngine,
        udp.domainName + (1,),
        udp.UdpTransport().openServerMode(('127.0.0.1', 162))
    )

    # UDP over IPv4, second listening interface/port
    config.addTransport(
        snmpEngine,
        udp.domainName + (2,),
        udp.UdpTransport().openServerMode(('127.0.0.1', 2162))
    )

    # SNMPv1/2c setup
    # SecurityName <-> CommunityName mapping
    config.addV1System(snmpEngine, 'my-area', 'public')


    TIMEOUT = 70.0
    lastTrapAt = time.time()


    # Register SNMP Application at the SNMP engine
    ntfrcv.NotificationReceiver(snmpEngine, cbFun)

    snmpEngine.transportDispatcher.jobStarted(1)  # this job would never finish

    # Create thread for Trap watcher
    thw = threading.Thread(target=watcher, name="watcher", args=(mc, msg,))
    thw.start()

    # Run I/O dispatcher which would receive queries and send confirmations
    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise
