import math
cells = {
    ' ': 0,
    'w': 1,
    'e': 2

}


class Cell:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f'{self.type}'






class Robot:
    def __init__(self, Pos, Rot, map):
        self.Robot_Pos = Pos
        self.Robot_Rot = Rot
        self.map = map
        self.SonarCallCount = 0
        self.PreviousSonarBits = 0
        self.ExitCell = [0, 0]

    def __repr__(self):
        return f'X = {self.Robot_Pos[1]}, Y = {self.Robot_Pos[0]}\n'


    def RobotRR(self):
        self.Robot_Rot = (self.Robot_Rot+1) % 6
        return 1

    def RobotRL(self):
        self.Robot_Rot = (self.Robot_Rot+5) % 6
        return 1

    def RobotGo(self):
        newPos = self.MapDisplacement(self.Robot_Pos, self.Robot_Rot)
        t = self.GetCellTypeOnNextStep(self.Robot_Pos, self.Robot_Rot)
        if t == 0:
            self.Robot_Pos = newPos
            self.SonarCallCount = 0
            self.PreviousSonarBits = 0
            return 1
        if t == 2:
            self.Robot_Pos = newPos
            self.SonarCallCount = 0
            self.PreviousSonarBits = 0
            return 2
        if t == 1:
            return 0

    def RobotSonar(self):
        sonarBits = 0
        if self.PreviousSonarBits % 2 == 1 or self.GetCellTypeInDirectionStep(self.Robot_Pos, self.Robot_Rot, self.SonarCallCount) == 1:
            sonarBits = 1
        if (self.PreviousSonarBits >> 1) % 2 == 1 or self.GetCellTypeInDirectionStep(self.Robot_Pos, (self.Robot_Rot + 5) % 6, self.SonarCallCount) == 1:
            sonarBits += 2
        if (self.PreviousSonarBits >> 2) % 2 == 1 or self.GetCellTypeInDirectionStep(self.Robot_Pos, (self.Robot_Rot + 1) % 6, self.SonarCallCount) == 1:
            sonarBits += 4
        if (self.PreviousSonarBits >> 3) % 2 == 1 or self.GetCellTypeInDirectionStep(self.Robot_Pos, (self.Robot_Rot + 4) % 6, self.SonarCallCount) == 1: #тип клетки
            sonarBits += 8
        if (self.PreviousSonarBits >> 4) % 2 == 1 or self.GetCellTypeInDirectionStep(self.Robot_Pos, (self.Robot_Rot + 2) % 6, self.SonarCallCount) == 1:
            sonarBits += 16
        self.PreviousSonarBits = sonarBits
        return sonarBits

    def GetCellTypeInDirectionStep(self, position, direction, callCount):
        for i in range(callCount+1):
            position = self.MapDisplacement(position, direction)
            return self.map[position[0]][position[1]].type

    def RobotCompass(self):
        ExitDirection = []
        ExitDirection.append(self.ExitCell[0] - self.Robot_Pos[0])
        ExitDirection.append(self.ExitCell[1] - self.Robot_Pos[1])
        CoordX = (self.ExitCell[0] - self.Robot_Pos[1])*math.cos(30*math.pi*2/360)
        CoordY = (self.ExitCell[1] + self.ExitCell[0]*0.495)-(self.Robot_Pos[1]+self.Robot_Pos[0]*0.495)

        CoordX = CoordX/math.sqrt(CoordX*CoordX + CoordY*CoordY)
        CoordY = CoordY / math.sqrt(CoordX * CoordX + CoordY * CoordY)
        angle = 0
        atg = math.atan2(CoordY, CoordX)*360/(math.pi*2)

        if CoordX ==0:
            if CoordY == 1:
                angle = 90
            elif CoordY == -1:
                angle =  270
        else:
            if CoordY > 0:
                angle = atg
            else:
                angle = atg + 360
        return angle*60

    def MapDisplacement(self, position, direction):
        disp = []
        if direction == 0:
            disp.append(position[0])
            disp.append(position[1]+1)

        elif direction == 1:
            disp.append(position[0]+1)
            disp.append(position[1])

        elif direction == 2:
            disp.append(position[0] + 1)
            disp.append(position[1]-1)

        elif direction == 3:
            disp.append(position[0])
            disp.append(position[1] - 1)

        elif direction == 4:
            disp.append(position[0] - 1)
            disp.append(position[1])

        elif direction == 5:
            disp.append(position[0] - 1)
            disp.append(position[1] + 1)

        return disp

    def GetCellTypeOnNextStep(self, currentPos, rot):
        pos = self.MapDisplacement(currentPos, rot)
        return self.map[pos[0]][pos[1]].type
