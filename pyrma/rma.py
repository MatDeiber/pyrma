from struct import unpack

# Updated 18/07/2021 MD: Rewrote BM pyrma script to increase performance

class RMA:
    def __init__(self,file):
        self.file = open(file, 'rb')
        self.header = self.file.read(1000).decode("utf-8")
        self.type = self.header[0:10]
        self.title = self.header[100:172]
        self.geometry = self.header[200:300]
        self.num_nodes = int(self.header[40:50])
        self.num_elements = int(self.header[50:60])
        
        self.time = None
        self.year = None
        self.xvel = {}
        self.yvel = {}
        self.zvel = {}
        self.depth = {}
        self.elevation = {}
        self.temperature = {}
        self.salinity = {}
        self.sussed = {}
        
        if self.type == 'RMA11     ':
            self.num_constits = int(self.header[60:70])
            if len(self.header[80:90].strip()) == 0:
                self.num_sedlayers = 0
            else:
                self.num_sedlayers = int(self.header[80:90])
            self.constit_name = []
            self.constit_name.append("NULL")
            i = 1
            print(self.num_constits)
            print(self.header[300:1000])
                        
            while i <= self.num_constits:
                # print self.header[300:400]
                self.constit_name.append(self.header[300 + (i - 1) * 8:308 + (i - 1) * 8])
                if self.header[300 + (i - 1) * 8:308 + (i - 1) * 8] == "   SSED ":
                    self.constit_name.append("  BSHEAR")
                    self.constit_name.append("BedThick")
                    j = 1
                    print(self.num_sedlayers)
                    while j <= self.num_sedlayers:
                        self.constit_name.append(" L%dThick" % j)
                        j = j + 1
                i = i + 1 
            self.constit = {}
            for i in range(1,self.num_constits + 1):
                self.constit[i] = {}
                
                
    def next(self,nodes=-1):  
        if nodes == -1:
            nodes = range(1, self.num_nodes+1)
                                        
        if self.type == 'RMA2      ':
            # WRITE(IRMAFM) TETT,NP,IYRR,((VEL(J,K),J=1,3),K=1,NP),(WSEL(J),J=1,NP),(VDOT(3,K),K=1,NP)
            t = self.file.read(12)
            
            if len(t) < 12:
                return False
            
            if t:
                a = unpack('fii', t)
                self.time = a[0]
                np = int(a[1])
                self.year = a[2]
                
                if (np != self.num_nodes):
                    print("Warning - NP (%d) on this timestep does not match header (%d)" % (np, self.num_nodes))
                fmt = '%df' % 5 * np
                
                b = unpack(fmt, self.file.read(20 * np))
                
                self.xvel = {node: b[(node - 1) * 3] for node in nodes}
                self.yvel = {node: b[(node - 1) * 3 + 1] for node in nodes}
                self.depth = {node: b[(node - 1) * 3 + 2] for node in nodes}
                self.elevation = {node: b[np * 3 + (node - 1)] for node in nodes }


        if self.type == 'RMA11     ':
            # READ(file1,END=100) TETT1,NQAL,NP,IYRR, ((VEL(K,J),J=1,NP),K=1,3), (wd(j),j=1,np), (wsel(j),j=1,np), ((TCON1(K,J),J=1,NP),K=1,NQAL-5)
            t = self.file.read(16)
            if len(t) < 16:
                return False
            
            if t:
                a = unpack('fiii', t)
                self.time = a[0]
                nqal = int(a[1])
                np = int(a[2])
                self.year = a[3]
                if ((nqal - 5) != (self.num_constits)):
                    print("Warning - NQAL-5 (%d) on this timestep does not match header (%d)" % (
                    nqal - 5, self.num_constits))
                if (np != self.num_nodes):
                    print("Warning - NP (%d) on this timestep does not match header (%d)" % (np, self.num_nodes))
                fmt = '%df' % nqal * np 
                b = unpack(fmt, self.file.read(4 * nqal * np))
                
                for c in range(1, self.num_constits + 1):
                    self.constit[c] = {node:b[np * ((c - 1) + 5) + (node - 1)] for node in nodes}
                    
                    
        if self.type == 'RMA10     ':
            # WRITE(IRMAFM) TETT,NP,NDF,NE,IYRR,((VSING(K,J),K=1,NDF),VVEL(J),WSLL(J),J=1,NP),(DFCT(J),J=1,NE),(VSING(7,J),J=1,NP)
            # WRITE(IRMAFM) TETT,NP,IYRR,((VEL(J,K),J=1,3),K=1,NP),(WSEL(J),J=1,NP),(VDOT(3,K),K=1,NP)
            t = self.file.read(20)
            if len(t) < 20:
                return False
            if t:
                a = unpack('fiiii', t)
                self.time = a[0]
                np = a[1]
                ndf = 6
                ne = a[3]
                self.year = a[4]
                if (np != self.num_nodes):
                    print("Warning - NP1 (%d) on this timestep does not match header (%d)" % (np, self.num_nodes))
                    
                tempRead = np * (3 + ndf) + ne
                fmt = '%df' % tempRead
                b = unpack(fmt, self.file.read(4 * tempRead))

                self.xvel = {node:b[(node - 1) * 8] for node in nodes}
                self.yvel = {node:b[1 + (node - 1) * 8] for node in nodes}
                self.depth = {node:b[2 + (node - 1) * 8] for node in nodes}
                self.salinity = {node:b[3 + (node - 1) * 8] for node in nodes}
                self.temperature = {node:b[4 + (node - 1) * 8] for node in nodes}
                self.sussed = {node:b[5 + (node - 1) * 8] for node in nodes}
                self.zvel = {node:b[6 + (node - 1) * 8] for node in nodes}
                self.elevation = {node:b[7 + (node - 1) * 8] for node in nodes}
                

        return True
