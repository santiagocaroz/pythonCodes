# -*- coding: utf-8 -*-


"""
Created on Sun Nov  7 23:37:09 2021

@author: Santiago Caro
"""

import numpy as np
import matplotlib.pyplot as plt

# import animatplot as amp
import pandas as pd
import scipy.signal as signal

class analisisTotal:
    def __init__(self,sujetos,analizar="si"):
        
        if analizar=="si":
            self.sujetos={"sujeto "+str(i+1):sujetos[i] for i in range(len(sujetos))}
            self.cineticasNorm=self.normalizacionTotal()
            # self.cineticasProm=self.promedioCineticas()
            self.primeraFase=self.divisionPeriodosEspecificos([(0,31),(0,31),(0,31),(0,31),(0,31)])
            self.segundaFase=self.divisionPeriodosEspecificos([(30,121),(30,121),(30,121),(30,121),(30,121)])
            # self.terceraFase=self.divisionPeriodos((120,151))
            self.terceraFase=self.divisionPeriodosEspecificos([(140,171),(130,161),(130,161),(130,161),(140,171)])
            # self.cuartaFase=self.divisionPeriodos((150,181))
            self.cuartaFase=self.divisionPeriodosEspecificos([(180,231),(150,201),(170,221),(150,201),(170,221)])
            self.quintaFase=self.divisionPeriodosEspecificos([(210,241),(200,231),(220,251),(200,231),(220,251)])
            # self.quintaFase=self.divisionPeriodos((230,260))
            # self.sextaFase=self.divisionPeriodos((210,-30))
            self.sextaFase=self.divisionPeriodosEspecificos([(210,-30),(210,-30),(210,-30),(210,-30),(210,-30)])
            self.octavaFase=self.divisionPeriodosEspecificos([(-30,None),(-30,None),(-30,None),(-30,None),(-30,None)])
            ###Organizar mejor
            
            self.promedio=[self.divisionPeriodos(self.sujetos[suj]) for suj in self.sujetos]
        else:
            pass
        
        
       
                    
    def addSujeto(self,sujeto):
        num=str(len(self.sujetos)+1)
        self.sujetos["sujeto "+num]=sujeto
    def normalizar(self,senal,tipo):
        if tipo=="F":
            offset=sum(senal)/len(senal)
            senal=[i-offset for i in senal]
        elif tipo=="C":
            pass
        maxim=max(senal)
        mini=min(senal)
        maxim=max([maxim,abs(mini)])
        senal=[i/maxim for i in senal]
        return senal
    
    def normalizacionTotal(self):
        cineticasNorm={"Time":{}}
        for i in self.sujetos:
            for var in self.sujetos[i].cineticas:
                if(var!="Time"):
                    if not(var in cineticasNorm):
                        cineticasNorm[var]={}
                    cineticasNorm[var][i]=self.normalizar(self.sujetos[i].cineticas[var],"C")
                else:
                    cineticasNorm["Time"][i]=self.sujetos[i].cineticas["Time"]
        return cineticasNorm
    
    def promedioCineticas(self,rango=(0,400)):
        promedio={var:self.cineticasNorm[var]["suj1"][rango[0]:rango[1]+1] for var in self.cineticasNorm}
        numSuj=len(self.cineticasNorm["Time"])
   
        for var in self.cineticasNorm:
            if var!="Time":
                for suj in self.cineticasNorm[var]:
                    if suj!="suj1":
                        promedio[var]=[promedio[var][i]+self.cineticasNorm[var][suj][i] for i in range(len(self.cineticasNorm[var][suj][rango[0]:rango[1]+1]))]
                promedio[var]=[i/numSuj for i in promedio[var]]
            else:
                promedio[var]=[i*1000 for i in range(rango[0],rango[1]+1) ]
            
        return promedio
    
    def freqxsubtramos(self, signal,time,d_i,d_f,tipo):
        time=time[d_i:d_f]
        signal=signal[d_i:d_f]
        # media=(max(signal)+min(signal))/2 
        # media=sum(signal)/len(signal)*1.005
        a=True
        
        if tipo=="PULSO":
            ndatosprom=3#Numero de datos a promediar
            limite=160
            contMax=2 #Maximo de frecuencias que superan el limite
            media=sum(signal)/len(signal)*1.05
        elif tipo=="RESP":
            media=sum(signal)/len(signal)
            ndatosprom=2
            limite=30
            contMax=1
        while a:
            bandUmb=0
            # cont=0
            periodos=[]
            freq=[]
            
            for i in range(len(signal)):
                if i>0:
                    if (signal[i]>signal[i-1] and bandUmb==0 and signal[i]>media):
                        bandUmb=1
                        # cont+=1
                        periodos.append(time[i])
                        # if signal[i]>media*1.1:
                            # cont-=1
                    elif (signal[i]<signal[i-1] and bandUmb==1 and signal[i]<media):
                        bandUmb=0
                    
            
            for i in range(len(periodos)):
                if i>=ndatosprom:
                    T=periodos[i]-periodos[i-ndatosprom]
                    T=T/(1000*ndatosprom)#conversión de ms a s y sacando el promedio
                    F=1/T
                    Fxmin=F*60
                    freq.append(Fxmin)
            conts=0
            
            for i in freq:
                if i>limite:
                    conts+=1
            if conts>=contMax:
                # print(f"vieja{media}")
                media=media*1.0025
                # print(media)
                # print("alto")
                # a=False

            else:
                a=False
        

        # plt.figure()
        # plt.plot(time,signal)
        # plt.axhline(y=media,linewidth=1)
  
        return [freq,media,periodos[ndatosprom:]]
    
    def freqxtramos(self, signal,time,d_i,d_f,divs,tipo,graph="off"): 
        # divs=5
        if d_f==None:
            d_f=len(signal)
            d_i=len(signal)+d_i
        elif d_f <0:
            d_f=len(signal)+d_f
        # print(d_f,d_i)
        dif=int((d_f-d_i)/divs)
        [freq,media,periodos]=[[],[],[]]
        for i in range(1,divs+1):
            if i==divs:
                [freq1,media1,periodos1]=self.freqxsubtramos(signal,time,d_i+(i-1)*dif,d_f,tipo)
                
            else:
                [freq1,media1,periodos1]=self.freqxsubtramos(signal,time,d_i+(i-1)*dif,d_i+i*dif,tipo)
            
            # print(len(freq1),len(periodos1))
            freq+=freq1
            media+=[media1]
            periodos+=periodos1
            
        if graph=="on":
            plt.figure()
            plt.plot(time,signal)
            for i in range(divs):
                plt.axhline(media[i],i*1/divs,(i+1)*1/divs, color="#8031FA")
            
        return [freq,media,periodos]
    
    def divisionPeriodos(self,sujeto,period=[0,31,121,171,231,261,-30,None]):
        # var="Speed"
        promedio={}
        maxim={}
        for var in sujeto.cineticas.keys():
            maxim[var]=round(max(sujeto.cineticas[var]),2)
            if not(var in promedio):
                promedio[var]=[]
            for i in range(len(period)-1):
                signal=sujeto.cineticas[var][period[i]:period[i+1]]
                promedio[var].append(round(sum(signal)/len(signal),2))
        return promedio,maxim
                
            
    
    def divisionPeriodosEspecificos(self,period=[(0,31),(0,31),(0,31),(0,31),(0,31)]):
        
        div={}
        for var in self.cineticasNorm:
            i=0
            div[var]={}
            for suj in self.cineticasNorm[var]:
                div[var][suj]=self.cineticasNorm[var][suj][period[i][0]:period[i][1]]
                i+=1
        # k=len(self.sujetos[suj].ADC_PULSO[0])/len(self.cineticasNorm["Time"][suj]) 
        
        i=0
        div2={}#ADC_PULSO
        
        for suj in self.sujetos:
            # print(suj)
            div2[suj]={}
            div2[suj]["PULSO"]=[]
            div2[suj]["RESP"]=[]
            
            k=len(self.sujetos[suj].ADC_PULSO[0])/len(self.cineticasNorm["Time"][suj]) 
            # print(k)
            if period[i][1]==None:
                period[i]=[int(period[i][0]*k),None]
            else:
                period[i]=[int(period[i][0]*k),int(period[i][1]*k)]
            div2[suj]["PULSO"].append(self.sujetos[suj].ADC_PULSO[0][period[i][0]:period[i][1]])
            div2[suj]["PULSO"].append(self.sujetos[suj].ADC_PULSO[1][period[i][0]:period[i][1]])
            div2[suj]["PULSO"].append(self.freqxtramos(self.sujetos[suj].ADC_PULSO[1],self.sujetos[suj].ADC_PULSO[0],period[i][0],period[i][1],5,"PULSO"))
            div2[suj]["RESP"].append(self.sujetos[suj].ADC_RESP[0][period[i][0]:period[i][1]])
            div2[suj]["RESP"].append(self.sujetos[suj].ADC_RESP[1][period[i][0]:period[i][1]])
            div2[suj]["RESP"].append(self.freqxtramos(self.sujetos[suj].ADC_RESP[1],self.sujetos[suj].ADC_RESP[0],period[i][0],period[i][1],3,"RESP"))
            
            i+=1
        
        return [div,div2]
               
class analisisXpersona(analisisTotal):
    
    def __init__(self,file, falta="no"):
        
        self.file=open(file,"r")
        # self.data=self.eliminarEnter()
        lstADCpulso, lstADCresp,strCinet=self.separacionVariables(self.eliminarEnter())
        
        cineticas=self.cineticXtime(strCinet)
        self.cineticas=self.separaCineticas(cineticas)
        init=self.cineticas["Time"][0]
        self.cineticas["Time"]=[i-init for i in self.cineticas["Time"]]
        if falta=="no":
            self.ADC_RESP=self.completeADC(lstADCresp,"RESP")
            self.ADC_PULSO=self.completeADC(lstADCpulso,"PULSO")
            self.Filt_RESP=self.filtro_pasabajas(self.ADC_RESP[1],self.ADC_RESP[0],0.5,10)
            self.Filt_PULSO=self.filtro_pasabajas(self.ADC_PULSO[1],self.ADC_PULSO[0],3.5,10)
        elif falta=="PULSO":
            self.ADC_RESP=self.completeADC(lstADCresp,"RESP")
            self.Filt_RESP=self.filtro_pasabajas(self.ADC_RESP[1],self.ADC_RESP[0],2,10)
    def eliminarEnter(self):
        lst=np.array(self.file.readlines())
        result=np.where(lst=="\n")
        for i in result[0][::-1]:
           lst=np.delete(lst,i)
        lst=list(lst)
        return lst
    def separacionVariables(self,data):
        listas=data
        listasADC=[]
        listasADCpulso=[]
        for i in range(len(listas)):
    
            indexResp=listas[i].find("ADC_RESP")
            indexPulse=listas[i].find("ADC_PULSO")
            # listasADC.append(listas[i][n:])
            # listas[i]=listas[i][:n]
            if(indexPulse>indexResp):
                listasADC.append(listas[i][indexResp:indexPulse])
                listasADCpulso.append(listas[i][indexPulse:])
                listas[i]=listas[i][:indexResp]
                
            elif indexPulse==-1:
                listasADC.append(listas[i][indexResp:])
                listas[i]=listas[i][:indexResp]
            elif indexResp==-1:
                listasADC.append(listas[i][indexPulse:])
                listas[i]=listas[i][:indexPulse]
            else:
                listasADC.append(listas[i][indexPulse:indexResp])
                listasADCpulso.append(listas[i][indexResp:])
                listas[i]=listas[i][:indexPulse]
        
        return listasADCpulso,listasADC,listas
    def cineticXtime(self,listas):
        for i in range(len(listas)):
            #Eliminación de corchetes
            listas[i]=listas[i].split("{")[1]
        #     listas[i]=listas[i].split("}\n")[0]
            listas[i]=listas[i].split(",") #Separar en parejas de datos [Variable,valor]
            listas[i].pop()
            for j in range(len(listas[i])):
                listas[i][j]=listas[i][j].split(":") #Separar la pareja de datos  
                listas[i][j][0]=listas[i][j][0].split('"')[1] #Eliminar comillas del nombre de la variable
            listas[i]=dict(listas[i]) #Conversión de listas a diccionarios
        return listas
    
    def separaCineticas(self,listas):        
        key=listas[0].keys()
        dicc={}
        for i in key:
            dicc[i]=[line[i] for line in listas]
        for i in dicc:
            dicc[i]=self.delComillas(dicc[i])
       
        # return listas
        return dicc
    def completeADC(self, lstADC,name="RESP"):
        for i in range(len(lstADC)):
    
            lstADC[i]=lstADC[i].split('ADC_'+name+'":')[1]
            lstADC[i]=lstADC[i].split('[')[1]
            if(lstADC[i].find(']}')!=-1):
                lstADC[i]=lstADC[i].split(']}')[0]
                lstADC[i]=lstADC[i].split(",")
                                
            elif (lstADC[i].find('],')!=-1):
                lstADC[i]=lstADC[i].split('],')[0]
                lstADC[i]=lstADC[i].split(",")
                # lstADC[i]=delComillas(lstADC[i])
            lstADC[i]=self.delComillas(lstADC[i])
        ADC=[]
        lenADC=[]
        for i in range(len(lstADC)-1):
            ADC+=lstADC[i+1]
            lenADC.append(len(lstADC[i+1]))
        tiempos=[]
        t=0
        for i in range(len(lenADC)):
            n=(self.cineticas["Time"][i+1]-self.cineticas["Time"][i])/lenADC[i]
            for j in range(lenADC[i]): 
                tiempos.append(t)
                t+=n
                # k+=1
        return [tiempos,ADC]
    
    def delComillas(self,lista):
        for i in range(len(lista)):
            if(lista[i].find('\\r\\n')!=-1):
                lista[i]=lista[i].split('\\r\\n')[0]
            
            if(lista[i].find('"')!=-1):
                try:
                    lista[i]=float(lista[i].split('"')[1])
                except:
                    lista[i]=lista[i]
            else:
                lista[i]=float(lista[i])
        return lista
        
    def frecuencia(self, signal, tiempos):
        S1=np.fft.fft(signal)
        N1 = len(S1)
        Fs1=1000/(tiempos[1]-tiempos[0]);
        F1 = np.arange(0,N1)*Fs1/N1 #Determinación del espectro de frecuencia
        plt.figure()
        plt.plot(F1,S1)
        plt.xlim(0,10)
        plt.ylim(-10,1e6)
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Amplitud')
        plt.title('Espectro de frecuencia')
        plt.grid('on')
        
    def filtro_pasabajas(self,senal,tiempos,fc,orden):
        Fs1=1000/(tiempos[1]-tiempos[0]);
        b, a = signal.butter(orden, fc/(Fs1/2), 'lowpass')
        FILT= signal.filtfilt(b,a,senal) 
        return [tiempos,FILT]
    
    
        

if __name__ == '__main__':
    analisis=analisisTotal([
        analisisXpersona("Pruebas mahavir\suj1.txt"),
        analisisXpersona("Pruebas mahavir\suj2.txt"),
        analisisXpersona("Pruebas mahavir\suj3.txt"),
        analisisXpersona("Pruebas mahavir\suj4.txt"),
        analisisXpersona("Pruebas mahavir\suj5.txt")
        ])
    
    # var="Speed"
    # for suj in analisis.cineticasNorm[var]:
    #     plt.plot(analisis.cineticasNorm["Time"][suj],analisis.cineticasNorm[var][suj])
    # plt.legend(analisis.cineticasNorm[var].keys())
    # freq=analisis.freqxtramos(analisis.sujetos["suj2"].Filt_RESP[1],analisis.sujetos["suj3"].Filt_RESP[0],0,3000)
    #################### 
    # fase=analisis.cuartaFase[0]
    # i=0
    # for var in fase:
        
    #     if (var!="Time" and var!="FC" and var!= "FR"):
    #         i+=1
    #         plt.subplot(2,2,i)
    #         # plt.figure()
    #         for suj in fase[var]:
    #             # plt.plot(fase["Time"][suj],fase[var][suj])
    #             if(var=="Cadence" and suj=="sujeto 3"):
    #                 fase[var][suj]=[i/0.55 for i in fase[var][suj]]
    #             plt.plot(range(len(fase[var][suj])),fase[var][suj])
    #         plt.legend(fase[var].keys())
    #         plt.ylim(-1,1)
    #         plt.title(var)
    #         plt.xlabel("time")
    
  
    fases=[analisis.primeraFase[1],analisis.segundaFase[1],analisis.terceraFase[1],analisis.cuartaFase[1],analisis.quintaFase[1],analisis.sextaFase[1],analisis.octavaFase[1]]
    # fases=[analisis.primeraFase[1]]
    variables=["RESP","PULSO"]
    for fasePulso in fases[5:6]:   
        for var in variables:
            c=0
            plt.figure()
            if var=="RESP":
                plt.suptitle("Señal respiratoria",fontsize=20)
                divs=3
            else:
                plt.suptitle("Señal cardíaca",fontsize=20)                
                divs=5     
            for suj in fasePulso:
                
                # p=[0,1,3,4,6,8]
                c+=1
                time=[i/1000 for i in fasePulso[suj][var][0]]
                plt.subplot(3,2,c)
                plt.plot(time,fasePulso[suj][var][1])
                # divs=3
                for i in range(divs):
                    plt.axhline(fasePulso[suj][var][2][1][i],i*1/divs,(i+1)*1/divs, color="#8031FA")
                plt.xlabel("Tiempo(s)",fontsize=20)
                plt.ylabel("ADC",fontsize=20)
                plt.legend([suj],fontsize=20,loc="upper right")
                plt.xticks(fontsize=20)
                plt.yticks(fontsize=20)
                plt.xlim(220,280)
                
    
    

    # for fasePulso in fases:   
    #     c=0
    #     plt.figure()
    #     for var in variables:
    #         c+=1
             
    #         plt.subplot(1,2,c) 
                
    #         for suj in fasePulso: 
                
                
    #             fasePulso[suj][var][2][2]=[i-fasePulso[suj][var][2][2][0] for i in fasePulso[suj][var][2][2]]
    #             plt.plot(fasePulso[suj][var][2][2], fasePulso[suj][var][2][0])
    #         plt.legend(fasePulso.keys())
    #         plt.xlabel("Time(ms)")
    #         if c==2:                
    #             plt.ylabel("Freq (bpm)")
    #             plt.title("Frecuencia cardíaca")
    #         else:
    #             plt.ylabel("Freq (rpm)")
    #             plt.title("Frecuencia respiratoria")
                
    # fisio={}
    # for i in range(len(fases)):          
    #     for suj in fases[i]:
    #         if i==0:
    #             fisio[suj]={}
    #         for var in fases[i][suj]:
    #             if i==0:
    #                 fisio[suj][var]=[fases[i][suj][var][2][0]]
    #             else:
    #                 fisio[suj][var].append(fases[i][suj][var][2][0])
      
            
    # import xlsxwriter
    # workbook = xlsxwriter.Workbook('Fisiologicas1.xlsx')
    # worksheet = workbook.add_worksheet()
    # fil=1
    # col=1
    # filp=8
    # for suj in fisio:
   
    #     for fase in fisio[suj]["RESP"]:
    #         prom=round(sum(fase)/len(fase),2)
    #         worksheet.write(fil,col, prom)
    #         col+=1
    #     fil+=1
    #     col=1
        
    #     for fase in fisio[suj]["PULSO"]:
    #         prom=round(sum(fase)/len(fase),2)
    #         worksheet.write(filp,col, prom)
    #         col+=1
    #     filp+=1
    #     col=1
        
    # workbook.close()
    
    
   
    
    