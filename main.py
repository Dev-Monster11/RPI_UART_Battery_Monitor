import math, sys, json, time

from PyQt5 import QtWidgets, QtCore, QtGui, QtSerialPort
from PyQt5.QtCore import QTimer, QDateTime


class Path(QtWidgets.QGraphicsPathItem):

    def __init__(self, source: QtCore.QPointF = None, destination: QtCore.QPointF = None, *args, **kwargs):
        super(Path, self).__init__(*args, **kwargs)
        self._sourcePoint = source
        self._destinationPoint = destination

    def setSource(self, point: QtCore.QPointF):
        self._sourcePoint = point

    def setDestination(self, point: QtCore.QPointF):
        self._destinationPoint = point

    def squarePath(self):
        s = self._sourcePoint
        d = self._destinationPoint

        mid_x = s.x() + ((d.x() - s.x()) * 0.5)

        path = QtGui.QPainterPath(QtCore.QPointF(s.x(), s.y()))
        path.lineTo(d.x(), d.y())

        return path

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:

        pen = QtGui.QPen()
        pen.setWidth(0)
        painter.setPen(pen)
        painter.setRenderHint(painter.Antialiasing)

        painter.setBrush(QtCore.Qt.NoBrush)

        path = self.squarePath()
        painter.drawPath(path)
        self.setPath(path)


class SquareButton(QtWidgets.QPushButton):
    TOP_POS = 'top'
    BOTTOM_POS = 'bottom'
    LEFT_POS = 'left'
    RIGHT_POS = 'right'

    def __init__(self,scene, x,y, input_text, output_text,box_name="SB", switch_name="SW",status_led_pos=BOTTOM_POS):
        super(SquareButton, self).__init__()
        self.rw = 80
        self.rh = 80
        self.w = 70
        self.h = 25
        self.status_led = SwitchLed(self.h ,self.h )
        self.switch_name = switch_name
        self.setIcon(QtGui.QIcon('icon/closed_switch.svg'))
        self.setIconSize(QtCore.QSize(self.w-10, self.h-10))
        self.setGeometry(x+(self.rw+20), y+((self.rh/2)-(self.h/2)), self.w, self.h)
        self.setStyleSheet("background-color: white;border-color:black;border-width: 1px;border-style: solid;")

        rectangle = QtWidgets.QGraphicsRectItem(QtCore.QRectF(x, y, self.rw, self.rh))
        rect_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(x+self.rw,y,x,y+self.rh))
        connect_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(
            x+self.rw,
            y+(self.rh/2),
            x+self.rw+20,
            (y+((self.rh/2)-(self.h/2)))+self.h/2
        ))
        box_name_text = QtWidgets.QGraphicsTextItem(box_name)
        box_name_text.setPos(x + (self.rw/2) - (box_name_text.boundingRect().size().width())/2, y - box_name_text.boundingRect().size().height() + 4)
        switch_name_text = QtWidgets.QGraphicsTextItem(switch_name)
        switch_name_text.setPos(x+(self.w+20) + switch_name_text.boundingRect().size().width(), y+((self.rh/2)-(self.h/2)) - switch_name_text.boundingRect().size().height() + 4)

        input_text = QtWidgets.QGraphicsTextItem(input_text)
        input_text.setPos(x+2,y+2)
        output_text = QtWidgets.QGraphicsTextItem(output_text)
        output_text.setPos(
            (x+self.rw)-output_text.boundingRect().size().width() - 2,
            (y+self.rh)-output_text.boundingRect().size().height() - 2)

        self.status_led.setGeometry(
            (x+(self.rw/2))-(self.h/2),y+(self.rh/2)-(self.h/2), self.h, self.h
        )

        self.scene = scene
        self.scene.addWidget(self)
        self.scene.addItem(rectangle)
        self.scene.addItem(rect_line)
        self.scene.addItem(connect_line)
        self.scene.addItem(box_name_text)
        self.scene.addItem(switch_name_text)
        self.scene.addItem(input_text)
        self.scene.addItem(output_text)
        self.scene.addWidget(self.status_led)

    def minimumSizeHint(self):
        return QtCore.QSize(self.w,self.h)

    def updateState(self):
        sled = self.getStatusLed()
        print(sled.getStatus())
        if sled.getStatus():
            print("set to off")
            self.setIcon(QtGui.QIcon('icon/closed_switch.svg'))
            sled.setOff()
        else:
            print("set to on")
            self.setIcon(QtGui.QIcon('icon/open_switch.png'))
            sled.setOn()

    def setStatus(self, status):
        sled = self.getStatusLed()
        if status == True:
            self.setIcon(QtGui.QIcon('icon/open_switch.png'))
            sled.setOn()
        if status == False:
            self.setIcon(QtGui.QIcon('icon/closed_switch.svg'))
            sled.setOff()

    def getStatusLed(self):
        return self.status_led

    def setClickHandler(self, function):
        self.clicked.connect(function)


class ValueBox(QtWidgets.QGraphicsRectItem):
    def __init__(self,scene, x, y, rw, rh):
        super(ValueBox, self).__init__()
        val_box = QtWidgets.QGraphicsRectItem(QtCore.QRectF(x, y, rw, rh))
        self.scene = scene
        self.scene.addItem(val_box)

class SwitchButton(QtWidgets.QPushButton):

    TOP_POS = 'top'
    BOTTOM_POS = 'bottom'
    LEFT_POS = 'left'
    RIGHT_POS = 'right'

    def __init__(self,scene, x,y, switch_name="SW", status_led_pos=BOTTOM_POS):
        super(SwitchButton, self).__init__()
        self.w = 70
        self.h = 25
        self.status_led = SwitchLed(self.h ,self.h )
        self.switch_name = switch_name
        self.setIcon(QtGui.QIcon('icon/closed_switch.svg'))
        self.setIconSize(QtCore.QSize(self.w-10, self.h-10))
        self.setGeometry(x, y, self.w, self.h)
        self.setStyleSheet("background-color: white;border-color:black;border-width: 1px;border-style: solid;")

        if status_led_pos==self.BOTTOM_POS:
            self.status_led.setGeometry(
                (self.x()+self.w/2)-self.h/2, self.y()+self.h+10, self.h, self.h
            )
        elif status_led_pos==self.LEFT_POS:
            self.status_led.setGeometry(
                self.x()-self.h-10,self.y(),self.h, self.h
            )

        switch_name = QtWidgets.QGraphicsTextItem(switch_name)
        switch_name.setPos(x + (self.w / 2) - (switch_name.boundingRect().size().width()) / 2,
                           y - switch_name.boundingRect().size().height() + 4)
        self.scene = scene
        self.scene.addItem(switch_name)
        self.scene.addWidget(self)
        self.scene.addWidget(self.status_led)

    def getTerminalPos(self,pos=LEFT_POS):

        if pos==self.TOP_POS:
            return QtCore.QPointF(self.x()+self.w/2, self.y())

        elif pos==self.BOTTOM_POS:
            return QtCore.QPointF(self.x()+self.w/2, self.y()+self.h)

        elif pos==self.LEFT_POS:
            pass

        elif pos==self.RIGHT_POS:
            pass

    def minimumSizeHint(self):
        return QtCore.QSize(self.w,self.h)

    def updateState(self):
        sled = self.getStatusLed()
        print(sled.getStatus())
        if sled.getStatus():
            print("set to off")
            self.setIcon(QtGui.QIcon('icon/closed_switch.svg'))
            sled.setOff()
        else:
            print("set to on")
            self.setIcon(QtGui.QIcon('icon/open_switch.png'))
            sled.setOn()

    def setStatus(self, status):
        sled = self.getStatusLed()
        if status == True:
            self.setIcon(QtGui.QIcon('icon/open_switch.png'))
            sled.setOn()
        if status == False:
            self.setIcon(QtGui.QIcon('icon/closed_switch.svg'))
            sled.setOff()
    def getStatusLed(self):
        return self.status_led

    def setClickHandler(self, function):
        self.clicked.connect(function)


class SwitchLed(QtWidgets.QLabel):

    def __init__(self,w,h):
        super(SwitchLed, self).__init__()
        self.status = False
        self.w = w
        self.h = h
        self.on_icon = QtGui.QIcon('icon/Button-Green.png')
        self.off_icon = QtGui.QIcon('icon/Button-Red.png')
        self.setStyleSheet("background: transparent;")
        #self.setGeometry(xpos, ypos, 30, 30)
        self.setOff()

    def getStatus(self):
        return self.status

    def setOn(self):
        self.status = True
        self.setPixmap(self.on_icon.pixmap(QtCore.QSize(self.w, self.h)))

    def setOff(self):
        self.status = False
        self.setPixmap(self.off_icon.pixmap(QtCore.QSize(self.w, self.h)))

class Logo(QtWidgets.QLabel):

    def __init__(self,scene,x,y,w, h):
        super(Logo, self).__init__()
        self.status = False
        self.w = w
        self.h = h
        self.icon = QtGui.QIcon('icon/logo.jpeg')
        self.setStyleSheet("background: transparent;")
        self.setGeometry(x, y, self.w, self.h)
        self.setPixmap(self.icon.pixmap(QtCore.QSize(self.w, self.h)))
        self.scene = scene
        self.scene.addWidget(self)

class Arrow(QtWidgets.QLabel):

    def __init__(self,scene,x,y,w, h):
        super(Arrow, self).__init__()
        self.status = False
        self.w = w
        self.h = h
        self.icon = QtGui.QIcon('icon/arrow.png')
        self.setStyleSheet("background: transparent;")
        self.setGeometry(x, y, self.w, self.h)
        self.setPixmap(self.icon.pixmap(QtCore.QSize(self.w, self.h)))
        self.scene = scene
        self.scene.addWidget(self)

class Resistor(QtWidgets.QLabel):

    def __init__(self,scene,x,y,w, h):
        super(Resistor, self).__init__()
        self.status = False
        self.w = w
        self.h = h
        self.icon = QtGui.QIcon('icon/resistor.png')
        self.setStyleSheet("background: transparent;")
        self.setGeometry(x, y, self.w, self.h)
        self.setPixmap(self.icon.pixmap(QtCore.QSize(self.w, self.h)))
        self.scene = scene
        self.scene.addWidget(self)

class Battery(QtWidgets.QLabel):

    def __init__(self,scene,x,y,w, h):
        super(Battery, self).__init__()
        self.status = False
        self.w = w
        self.h = h
        self.icon = QtGui.QIcon('icon/battery.png')
        self.setStyleSheet("background: transparent;")
        self.setGeometry(x, y, self.w, self.h)
        self.setPixmap(self.icon.pixmap(QtCore.QSize(self.w, self.h)))
        self.scene = scene
        self.scene.addWidget(self)

class ViewPort(QtWidgets.QGraphicsView):

    def __init__(self):
        super(ViewPort, self).__init__()
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setFixedSize(1024, 720) #Optimal 1024, 600
        self.build_schematic()
        self.setMouseTracking(True)

    def build_schematic(self):

        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setSceneRect(0, 0, 1024, 650)

        line1 = Path(source=QtCore.QPoint(0,0), destination=QtCore.QPoint(1024,600))
        line2 = Path(source=QtCore.QPoint(0, 0), destination=QtCore.QPoint(350, 116))


        #self.button_isb = SwitchButton(self.scene, 300,400,status_led_pos=SwitchButton.LEFT_POS)
        #self.button_isb.setClickHandler(self.handle_click)

        #self.button_isb2 = SwitchButton(self.scene, 100,100)
        #self.button_isb2.setClickHandler(self.handle_click2)

        # logo
        logo = Logo(self.scene,490,25,90,55)

        # wire
        main_line1 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(475,92,475,522))
        main_line2 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(570, 120, 570, 522))
        ic1_main_line1 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(250,92,475,92))

        ic5_main_line1 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(370,422,475,422))
        ic6_main_line1 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(370,522,475,522))

        box1_main_line1 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(350,218,600,218))
        box2_main_line1 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(350, 318, 475, 318))

        ic7_main_line2 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(570,120,600,120))
        ic11_main_line2 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(570,302,700,302))
        ic12_main_line2 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(570,422,600,422))
        ic13_main_line2 = QtWidgets.QGraphicsLineItem(QtCore.QLineF(570, 522, 600, 522))

        ic2_box1_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(130,222,180,222))
        ic4_box2_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(130,322,180,322))

        ic7_box3_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(670,122,680,122))
        ic9_box4_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(670,222,680,222))

        #ic8_box3_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(880,119,850,119))
        ic10_box4_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(880,219,850,219))
        ic11_box4ic10_line_a = QtWidgets.QGraphicsLineItem(QtCore.QLineF(770, 302, 865, 302))
        ic11_box4ic10_line_b = QtWidgets.QGraphicsLineItem(QtCore.QLineF(865, 302, 865, 219))

        ic12_box5_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(670,420,680,420))
        ic13_box6_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(670,520,680,520))

        ic5_resistor_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(300, 422, 250, 422))
        ic6_resistor_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(300, 522, 250, 522))

        resistor = Resistor(self.scene,180,412,70,20)
        battery = Battery(self.scene, 202, 507, 70, 30)

        self.scene.addItem(main_line1)
        self.scene.addItem(main_line2)
        self.scene.addItem(ic1_main_line1)
        self.scene.addItem(ic5_main_line1)
        self.scene.addItem(ic6_main_line1)
        self.scene.addItem(box1_main_line1)
        self.scene.addItem(box2_main_line1)

        self.scene.addItem(ic7_main_line2)
        self.scene.addItem(ic11_main_line2)
        self.scene.addItem(ic12_main_line2)
        self.scene.addItem(ic13_main_line2)

        self.scene.addItem(ic2_box1_line)
        self.scene.addItem(ic4_box2_line)

        self.scene.addItem(ic7_box3_line)
        self.scene.addItem(ic9_box4_line)

        #self.scene.addItem(ic8_box3_line)
        self.scene.addItem(ic10_box4_line)
        self.scene.addItem(ic11_box4ic10_line_a)
        self.scene.addItem(ic11_box4ic10_line_b)

        self.scene.addItem(ic12_box5_line)
        self.scene.addItem(ic13_box6_line)

        self.scene.addItem(ic5_resistor_line)
        self.scene.addItem(ic6_resistor_line)

        # init and paint component
        # left
        self.ic_1 = SwitchButton(self.scene, 180, 80,status_led_pos=SwitchButton.BOTTOM_POS,switch_name="IS8")
        self.ic_2 = SwitchButton(self.scene, 60, 210,status_led_pos=SwitchButton.BOTTOM_POS,switch_name="IC1")
        #self.ic_2.setClickHandler(self.box_1_handler)
        self.ic_3 = SwitchButton(self.scene, 454, 255, status_led_pos=SwitchButton.LEFT_POS,switch_name="IS9")
        self.ic_5 = SwitchButton(self.scene, 300, 410, status_led_pos=SwitchButton.BOTTOM_POS, switch_name="IC8")
        self.ic_6 = SwitchButton(self.scene, 300, 510, status_led_pos=SwitchButton.BOTTOM_POS, switch_name="IC3")

        #right
        self.ic_7 = SwitchButton(self.scene, 600, 110,status_led_pos=SwitchButton.BOTTOM_POS, switch_name="IC4")
        #self.ic_8 = SwitchButton(self.scene, 880, 107, status_led_pos=SwitchButton.BOTTOM_POS)
        #self.ic_8.setClickHandler(self.ic_8_handler)
        self.ic_9 = SwitchButton(self.scene, 600, 210,status_led_pos=SwitchButton.BOTTOM_POS, switch_name="IC5")
        self.ic_10 = SwitchButton(self.scene, 880, 207, status_led_pos=SwitchButton.BOTTOM_POS, switch_name="IS10")
        self.ic_11 = SwitchButton(self.scene, 700, 290, status_led_pos=SwitchButton.BOTTOM_POS, switch_name="C0")

        self.ic_12 = SwitchButton(self.scene, 600, 410, status_led_pos=SwitchButton.BOTTOM_POS, switch_name="IC6")
        self.ic_13 = SwitchButton(self.scene, 600, 510, status_led_pos=SwitchButton.BOTTOM_POS, switch_name="IC7")

        self.ic_14 = SwitchButton(self.scene, 60, 310, status_led_pos=SwitchButton.BOTTOM_POS, switch_name="IC2")

        self.box_1 = SquareButton(self.scene, 180, 180, "", "", box_name="RD1",switch_name="") #x:470
        self.box_2 = SquareButton(self.scene, 180, 280, "", "", box_name="RD2",switch_name="") #x:470

        self.box_3 = SquareButton(self.scene, 680, 80, "", "", box_name="INV1",switch_name="IS4")
        self.box_4 = SquareButton(self.scene, 680, 180, "", "", box_name="REG1",switch_name="IS5")
        self.box_5 = SquareButton(self.scene, 680, 380, "", "", box_name="CV1",switch_name="IS6")
        self.box_6 = SquareButton(self.scene, 680, 480, "", "", box_name="CV2",switch_name="IS7")

        #value boxes right 
        val_box_1 = ValueBox(self.scene, 940, 105, 70, 30)
        val_box_2 = ValueBox(self.scene, 940, 259, 70, 30)
        val_box_3 = ValueBox(self.scene, 940, 452, 70, 30)

        #value boxes left 
        val_box_4 = ValueBox(self.scene, 60, 150, 70, 30)
        val_box_5 = ValueBox(self.scene, 279, 254, 70, 30)
        val_box_6 = ValueBox(self.scene, 279, 152, 70, 30)

        #value box lines

        is4_vb1_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(850,119,911,119))
        is6_vb3_line_a = QtWidgets.QGraphicsLineItem(QtCore.QLineF(850,418,880,418))
        is7_vb3_line_b = QtWidgets.QGraphicsLineItem(QtCore.QLineF(850,518,880,518))
        is6_vb3_line_c = QtWidgets.QGraphicsLineItem(QtCore.QLineF(880,418,880,518))
        is6_vb3_line_d = QtWidgets.QGraphicsLineItem(QtCore.QLineF(880,468,922,467))

        vb4_ic1_line_a = QtWidgets.QGraphicsLineItem(QtCore.QLineF(26,165,60,165))
        vb4_ic1_line_b = QtWidgets.QGraphicsLineItem(QtCore.QLineF(26,223,60,223))
        vb4_ic1_line_c = QtWidgets.QGraphicsLineItem(QtCore.QLineF(26,322,60,322))
        vb4_ic1_line_d = QtWidgets.QGraphicsLineItem(QtCore.QLineF(26,165,26,322))

        is6_vb3_line_d_arrow = Arrow(self.scene, 920, 462, 10, 10) 
        is4_vb1_arrow = Arrow(self.scene, 909, 114, 10, 10) 

        self.scene.addItem(is4_vb1_line)
        self.scene.addItem(is6_vb3_line_a)
        self.scene.addItem(is7_vb3_line_b)
        self.scene.addItem(is6_vb3_line_c)
        self.scene.addItem(is6_vb3_line_d)

        self.scene.addItem(vb4_ic1_line_a)
        self.scene.addItem(vb4_ic1_line_b)
        self.scene.addItem(vb4_ic1_line_c)
        self.scene.addItem(vb4_ic1_line_d)


        #nav buttons

        #self.mainBtn = QtWidgets.QPushButton('Main', self)
        #self.mainBtn.setStyleSheet("font: 25px;")
        #self.mainBtn.clicked.connect(self.navigateToMain)
        #self.mainBtn.move(2,610)

        self.setBtn = QtWidgets.QPushButton('Impostazioni', self)
        self.setBtn.setStyleSheet("font: 28px;")
        self.setBtn.clicked.connect(self.navigateToSettings)
        self.setBtn.move(42,630)

        self.maintenanceBtn = QtWidgets.QPushButton('Misure', self)
        self.maintenanceBtn.setStyleSheet("font: 28px;")
        self.maintenanceBtn.clicked.connect(self.navigateToMaintenance)
        self.maintenanceBtn.move(220,630)

        self.alarmBtn = QtWidgets.QPushButton('Allarmi', self)
        self.alarmBtn.setStyleSheet("font: 28px;")
        self.alarmBtn.clicked.connect(self.navigateToAlarm)
        self.alarmBtn.move(324,630)

        #self.dateLabel = ShowDate(self.scene) 

        self.setScene(self.scene)
        
        self.getSwitchData()

    def navigateToMain(self):
        pass
        #widgets.setCurrentIndex(widgets.currentIndex() + 1)

    def navigateToSettings(self):
        widgets.setCurrentIndex(widgets.currentIndex() + 1)

    def navigateToMaintenance(self):
        widgets.setCurrentIndex(widgets.currentIndex() + 2)

    def navigateToAlarm(self):
        widgets.setCurrentIndex(widgets.currentIndex() + 3)

    def navigateToBattery(self):
        widgets.setCurrentIndex(widgets.currentIndex() + 4)

    def getSwitchData(self):

        self.getDataFromFile()
        self.ic_1.setStatus(self.statusList[self.ic_1.switch_name])
        self.ic_2.setStatus(self.statusList[self.ic_2.switch_name])
        self.ic_3.setStatus(self.statusList[self.ic_3.switch_name])
        #self.ic_4.setStatus(self.statusList[self.ic_4.switch_name])
        self.ic_5.setStatus(self.statusList[self.ic_5.switch_name])
        self.ic_6.setStatus(self.statusList[self.ic_6.switch_name])
        self.ic_7.setStatus(self.statusList[self.ic_7.switch_name])
        #self.ic_8.setStatus(self.statusList[self.ic_8.switch_name])
        self.ic_9.setStatus(self.statusList[self.ic_9.switch_name])
        self.ic_10.setStatus(self.statusList[self.ic_10.switch_name])
        self.ic_11.setStatus(self.statusList[self.ic_11.switch_name])
        self.ic_12.setStatus(self.statusList[self.ic_12.switch_name])
        self.ic_13.setStatus(self.statusList[self.ic_13.switch_name])

    def getDataFromFile(self):

        self.statusList = {}
        with open('./status.json') as f:
            self.statusList = json.loads(f.read())

    def mouseMoveEvent(self, event): 
        print('mouseMoveEvent: pos {}'.format(event.pos()))
        pass

class ShowDate(QtWidgets.QGraphicsTextItem):

    def __init__(self, scene):
        super(ShowDate, self).__init__()
        self.dateLabel = QtWidgets.QGraphicsTextItem(self)
        timer = QTimer(self)
        timer.timeout.connect(self.updateTime)
        timer.start()
        self.dateLabel.setPos(750, 630)

        self.scene = scene
        self.scene.addItem(self.dateLabel)

    def updateTime(self):
        datetime = QDateTime.currentDateTime() 
        currentdate = datetime.toString()
        self.dateLabel.setPlainText("    " + currentdate);



class SettingView(QtWidgets.QGraphicsView):
    def __init__(self):
        super(SettingView, self).__init__()
        self.mainBtn = QtWidgets.QPushButton('Main', self)
        self.mainBtn.setStyleSheet("font: 25px;")
        self.mainBtn.clicked.connect(self.navigateToMain)
        self.mainBtn.move(2,600)
    def createTable(self):
        self.table = QtWidgets.QTableWidget(self)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.setRowCount(4)
        self.table.setColumnCount(2)
        self.table.setMinimumWidth(1000)
        self.table.setMinimumHeight(500)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(["ID","Nome", "Valore", "Unita", "Descrizione"])        

    def navigateToMain(self):
        widgets.setCurrentIndex(widgets.currentIndex() - 1)

class MaintenanceView(QtWidgets.QGraphicsView):
    def __init__(self):
        super(MaintenanceView, self).__init__()

        self.mainBtn = QtWidgets.QPushButton('Main', self)
        self.mainBtn.setStyleSheet("font: 25px;")
        self.mainBtn.clicked.connect(self.navigateToMain)
        self.createTable()
        self.mainBtn.move(2,600)

        self.combo = QtWidgets.QComboBox(self)
        self.combo.addItem("RD1")
        self.combo.addItem("RD2")
        self.combo.addItem("CIV1")
        self.combo.addItem("CIV2")
        self.combo.addItem("DCREG")
        self.combo.addItem("BATT")
        self.combo.addItem("INV")

        self.combo.move(833, 13)
        self.combo.activated[str].connect(self.onChanged)      
        self.combo.show()

    def createTable(self):
        self.table = QtWidgets.QTableWidget(self)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.setRowCount(4)
        self.table.setColumnCount(5)
        self.table.setMinimumWidth(1000)
        self.table.setMinimumHeight(500)

        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

        self.table.setHorizontalHeaderLabels(["ID", "NOME", "VALORE", "UNITÀ","DESCRIZIONE"])

        self.table.setItem(0, 0, QtWidgets.QTableWidgetItem("1"))
        self.table.setItem(0, 1, QtWidgets.QTableWidgetItem("V1"))
        self.table.setItem(0, 2, QtWidgets.QTableWidgetItem("110"))

        self.table.setItem(1, 0, QtWidgets.QTableWidgetItem("2"))
        self.table.setItem(1, 1, QtWidgets.QTableWidgetItem("V1"))
        self.table.setItem(1, 2, QtWidgets.QTableWidgetItem("110"))

        self.table.setItem(2, 0, QtWidgets.QTableWidgetItem("3"))
        self.table.setItem(2, 1, QtWidgets.QTableWidgetItem("V1"))
        self.table.setItem(2, 2, QtWidgets.QTableWidgetItem("110"))

        self.table.setItem(3, 0, QtWidgets.QTableWidgetItem("4"))
        self.table.setItem(3, 1, QtWidgets.QTableWidgetItem("V1"))
        self.table.setItem(3, 2, QtWidgets.QTableWidgetItem("110"))

        self.table.move(5,50)

    def onChanged(self, text):
        pass

    def navigateToMain(self):
        widgets.setCurrentIndex(widgets.currentIndex() - 2)

class AlarmView(QtWidgets.QGraphicsView):
    def __init__(self):
        super(AlarmView, self).__init__()
        self.mainBtn = QtWidgets.QPushButton('Menu', self)
        self.mainBtn.setStyleSheet("font: 25px;")
        self.mainBtn.clicked.connect(self.navigateToMain)
        self.createTable()
        self.mainBtn.move(2,600)

    def createTable(self):
        self.table = QtWidgets.QTableWidget(self)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.setRowCount(4)
        self.table.setColumnCount(2)
        self.table.setMinimumWidth(1000)
        self.table.setMinimumHeight(500)

        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.table.setHorizontalHeaderLabels(["ID","DESCRIZIONE ALLARME"])

        self.table.setItem(0, 0, QtWidgets.QTableWidgetItem("2"))
        self.table.setItem(0, 1, QtWidgets.QTableWidgetItem("V RADDRIZZATORE ALTA"))

        self.table.move(5,50)

    def navigateToMain(self):
        widgets.setCurrentIndex(widgets.currentIndex() - 3)


class BoardComm():
    def __init__(self):
        self.com = QtSerialPort.QSerialPort(
            '/dev/ttyS1',
            readyRead=self.receive,

        )
    def readData(comm):
        pass
    def receive():
        print(self.com.readAll())
    def openPort(self):
        if self.com.open(QIODevice.ReadWrite):
            self.com.setBaudRate(QtSerialPort.QSerialPort.Baud115200)
            self.com.setDataBits(QtSerialPort.QSerialPort.Data8)
            self.com.setStopBit(QtSerialPort.QSerialPort.OneStop)
            self.com.setParity(QtSerialPort.QSerialPort.NoParity)
            self.serial.readyRead.connect(self.receive)
    def startComm(self):
        # while True: 
            #recieve = readData(comm)
            self.comm.write("asdfasdf")
            #print(recieve)
    
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    window = ViewPort()
    setting_view = SettingView()
    maintenance_view = MaintenanceView()
    alarm_view = AlarmView()

    widgets = QtWidgets.QStackedWidget()
    widgets.addWidget(window)
    widgets.addWidget(setting_view)
    widgets.addWidget(maintenance_view)
    widgets.addWidget(alarm_view)

    widgets.setFixedHeight(720)
    widgets.setFixedWidth(1024)

    widgets.show()

    timer = QtCore.QTimer()
    timer.timeout.connect(window.getSwitchData)
    timer.setInterval(1000)
    timer.start()

    boardcom = BoardComm()
    boardcom.startComm()
    sys.exit(app.exec())
