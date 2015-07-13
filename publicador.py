# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from gui.wPublicador import Ui_Form
from data.conexion2 import Data
from crawlers.sexday import FormPage
from dialogo import wDialogo
from agregar_anuncio import wAgregar_anuncio

from threading import Thread

class wPublicador(QWidget, Ui_Form):
    def __init__(self, parent= None):
        super(wPublicador, self).__init__(parent)
        self.setupUi(self)
        #Decracion de variables globales.
        self.listaProvincias = []
        self.__fillFormularios()
        self.__fillAnuncios()
        self.cbFormulario.currentIndexChanged['int'].connect(self.changeForm)
        self.comboCredencial.currentIndexChanged['int'].connect(self.changeCredencial)
        self.comboMetaAdi.currentIndexChanged['int'].connect(self.changeMetaAdi)


    def __fillAnuncios(self):
        self.modelAnuncios = QStandardItemModel(0,2,self.tableAnuncios)
        self.modelAnuncios.setHorizontalHeaderItem(0, QStandardItem('Codigo'))
        self.modelAnuncios.setHorizontalHeaderItem(1, QStandardItem('Descripcion'))
        self.tableAnuncios.setModel(self.modelAnuncios)

    def __fillFormularios(self):
        #rellena el combobox de formularios
        db = Data.Instance()
        qry = db.consultar('select idFormulario,descripcion from formulario')
        while(qry.next()):
            self.cbFormulario.addItem(qry.value(1), QVariant(qry.value(0)))
        self.cbFormulario.setCurrentIndex(-1)


    def __filterAnuncios(self, filtro):
        self.model.setFilter("titulo like '%"+filtro+"%'" )
        self.model.select()


    def __fillCredencial(self):
        db = Data.Instance()
        qry = db.consultar('select * from credencial')
        while(qry.next()):
            self.comboCredencial.addItem(qry.value(1),QVariant(qry.value(0)))

    def __fillMetaAdi(self):
        db = Data.Instance()
        qry = db.consultar('select * from tags')
        while(qry.next()):
            self.comboMetaAdi.addItem(qry.value(1),QVariant(qry.value(0)))

    def __fillCiudades(self):
        self.modelCiudad = QStandardItemModel(self.listCiudad)
        lista = self.crl.getCiudades()
        for ciudad in lista:
            item = QStandardItem(ciudad.text)
            self.modelCiudad.appendRow(item)
        self.listCiudad.setModel(self.modelCiudad)

    def __fillProvincias(self, ciudad):
        self.modelProvincia = QStandardItemModel(self.listProvincia)
        lista = self.crl.getProvincias(ciudad)
        for provincia in lista:
            item = QStandardItem(provincia.text)
            item.setCheckable(True)
            self.modelProvincia.appendRow(item)
        self.listProvincia.setModel(self.modelProvincia)

    def __fillCategorias(self):
        self.modelCategorias = QStandardItemModel(self.listProvincia)
        lista = self.crl.getCategorias()
        for categoria in lista:
            item = QStandardItem(categoria.text)
            item.setCheckable(True)
            self.modelCategorias.appendRow(item)
        self.listCategorias.setModel(self.modelCategorias)


    def __guardarProvincias(self,CiudadIndex):
        if hasattr(self, 'modelProvincia'):
            for index in range(self.modelProvincia.rowCount()):
                item = self.modelProvincia.item(index)
                if item.isCheckable() and item.checkState() == Qt.Checked:
                    CiudadProvincia = {}
                    CiudadProvincia['Ciudad'] = CiudadIndex
                    CiudadProvincia['Provincia'] = item.row()
                    print('Ciudad: '+ str(CiudadProvincia['Ciudad'])+ ' Provincia:' +str(CiudadProvincia['Provincia']))
                    self.listaProvincias.append(CiudadProvincia)

    def __guardarCategorias(self):

        for index in range(self.modelCategorias.rowCount()):
            item = self.modelCategorias.item(index)
            if item.checkState() == Qt.Checked:
                self.listaCategorias.append(item.row())


    def __crearLote(self):
        pass


    @pyqtSlot(QModelIndex)
    def on_listCiudad_clicked(self,index):
        print('Ciudad: '+ str(index.row()))
        self.__guardarProvincias(index.row())
        self.ciudadSeleccionada = index.row()
        self.__fillProvincias(index.row())


    @pyqtSlot(QModelIndex)
    def on_listProvincia_clicked(self,index):
        print('Provincia: ' + str(index.row()))
        self.provinciaSeleccionada = index.row()

    @pyqtSlot(QModelIndex)
    def on_listCategorias_clicked(self,index):
        print('Categoria: '+ str(index.row()))
        self.categoriaSeleccionada = index.row()

    @pyqtSlot()
    def on_cbCredencial_clicked(self):
        if(self.cbCredencial.isChecked()):
            self.__fillCredencial()
            self.lblCredencial.setEnabled(True)
            self.comboCredencial.setEnabled(True)
        else:
            self.lblCredencial.setEnabled(False)
            self.comboCredencial.setEnabled(False)

    @pyqtSlot()
    def on_cbTagAdi_clicked(self):
        if(self.cbTagAdi.isChecked()):
            self.__fillMetaAdi()
            self.lblMetaAdi.setEnabled(True)
            self.comboMetaAdi.setEnabled(True)
        else:
            self.lblMetaAdi.setEnabled(False)
            self.comboMetaAdi.setEnabled(False)

    def changeCredencial(self,index):
        print(str(self.comboCredencial.itemData(index)))

    def changeMetaAdi(self,index):
        print(str(self.comboMetaAdi.itemData(index)))

    def changeForm(self,index):
        #Seleccion de formularios
        print(str(self.cbFormulario.itemData(index)))

        if int(self.cbFormulario.itemData(index)) == 1:
            #Sexday.es
            #dialogo = wDialogo()
            #dialogo.anunciar('Atencios', 'Por favor espere mientras se cargan las ciudades')
            self.crl = FormPage() #Cargar el crawler
            self.__fillCiudades()
            self.__fillCategorias()

    @pyqtSlot(QModelIndex)
    def on_listProvincia_clicked(self,index):
        item = self.modelProvincia.item(index.row())
        if item.checkState() == Qt.Unchecked:
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)

    @pyqtSlot(QModelIndex)
    def on_listCategorias_clicked(self,index):
        item = self.modelCategorias.item(index.row())
        if item.checkState() == Qt.Unchecked:
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)

    @pyqtSlot(str)
    def on_txtFilter_textChanged(self,text):
        self.__filterAnuncios(text)

    @pyqtSlot()
    def on_btnAgregar_clicked(self):
        window = wAgregar_anuncio()
        if window.exec_():
            print(window.datos['codigo'])
            print(window.datos['descripcion'])
            self.modelAnuncios.appendRow([QStandardItem(str(window.datos['codigo'])),QStandardItem(window.datos['descripcion'])])

    @pyqtSlot()
    def on_btnEliminar_clicked(self):
        indexes = self.tableAnuncios.selectedIndexes()
        self.modelAnuncios.removeRow(indexes[0].row())

    @pyqtSlot()
    def on_btnProcesar_clicked(self):
        #ver el diccionario
        self.__guardarProvincias(self.ciudadSeleccionada)
        for x in self.listaProvincias:
            print('Ciudad: ' + str(x['Ciudad']))
            print('Provincia: ' + str(x['Provincia']))
        #Aca se envia la data.
        #FormPage().fill_form(data).submit()
