#ifndef THKBACKUP_H
#define THKBACKUP_H

#include <QString>
#include <QHash>
#include <ctime>
#include <QSettings>
#include "tabstractparamscomputer.h"
#include "tsinglebackup.h"
#include <QFile>

class TAbstractParametersTable;

/***************************************************************************************************/
/*
  Example d'utilisation de la classe :
  Declaration :
    hkBackup = new THKBackup();
    // ajout des elements qui vont faire partie de la sauvegarde

    QList<quint32> voltagesHKList;
    voltagesHKList << DEBUG_ANALYSER_TF_ID
                   << DEBUG_BOTTOM_DEFLECTOR_TF_ID
                   << DEBUG_TOP_DEFLECTOR_TF_ID
                   << DEBUG_TOP_HAT_TF_ID;

    hkBackup->addMultipleHKFromDescription(voltagesHKList,TSingleBackup::AutoXDataTime,"");


    hkBackup->addHKFromDescription(OBC_Board_Temp_TF_ID);
    hkBackup->addHKFromDescription(UGTI_V_V_ICS_TF_ID);
    hkBackup->addHKFromDescription(UGTI_V_I_ICS_TF_ID);
    hkBackup->addHKFromDescription(UGTI_ICS_Level_ID);

    for (int i = 0; i < 39; i++)
    {
        hkBackup->addHK(UGTI_Temperature_C1_V1_TF_ID+i,TSingleBackup::Double,1,tfComputer->dispName(UGTI_Temperature_C1_V1_ID+i), tfComputer->realName(UGTI_Temperature_C1_V1_ID+i),tfComputer->unit(UGTI_Temperature_C1_V1_ID+i),TSingleBackup::PrivateXDataTime,"");
        hkBackup->addHK(UGTI_V_C1_V1_ID+i,TSingleBackup::Double,1,tfComputer->dispName(UGTI_V_C1_V1_ID+i), tfComputer->realName(UGTI_V_C1_V1_ID+i),tfComputer->unit(UGTI_V_C1_V1_ID+i),TSingleBackup::PrivateXDataTime,"");
    }
    hkBackup->addHK(UGTI_Temp_Servitude_ID,TSingleBackup::Double,1,tfComputer->dispName(UGTI_Temp_Servitude_ID), tfComputer->realName(UGTI_Temp_Servitude_ID), tfComputer->unit(UGTI_Temp_Servitude_ID),TSingleBackup::PrivateXDataTime,"");
    hkBackup->addHK(UGTI_Temp_OBC_ID,TSingleBackup::Double,1,tfComputer->dispName(UGTI_Temp_OBC_ID), tfComputer->realName(UGTI_Temp_OBC_ID), tfComputer->unit(UGTI_Temp_OBC_ID),TSingleBackup::PrivateXDataTime,"");
    hkBackup->addHK(UGTI_Temp_Convertisseurs_ID,TSingleBackup::Double,1,tfComputer->dispName(UGTI_Temp_Convertisseurs_ID), tfComputer->realName(UGTI_Temp_Convertisseurs_ID), tfComputer->unit(UGTI_Temp_Convertisseurs_ID),TSingleBackup::PrivateXDataTime,"");


    sauvegarde :
        double date = ...;

                hkBackup->saveDataXY(UGTI_Temp_Servitude_ID,&date,&UGTI_Temp_Servitude,1);
                hkBackup->saveDataXY(UGTI_Temp_OBC_TF_ID,&date,&UGTI_Temp_OBC_TF,1);
                hkBackup->saveDataXY(UGTI_Temp_Convertisseurs_TF_ID,&date,&UGTI_Temp_Convertisseurs_TF,1);


        hkBackup->startMultipleSaveWithSameDatation();
        hkBackup->saveData(OBC_Board_Temp_TF_ID,&OBC_Board_Temp_TF,1);
        hkBackup->saveData(UGTI_V_V_ICS_TF_ID,&UGTI_V_V_ICS_TF,1);
        hkBackup->saveData(UGTI_V_I_ICS_TF_ID,&UGTI_V_I_ICS_TF,1);
        hkBackup->saveData(UGTI_ICS_Level_ID,&UGTI_ICS_Level,1);
        hkBackup->stopMultipleSaveWithSameDatation();

*/

const quint32 defaultFileSize = 200*1024*1024;// 200 Mo

class TSingleHkBackup
{
public:
    enum BackupOptions {
        NoXData, // pas de données X spécifiées sera plotté avec des index sur X
        ExternXData, // utilisation du fichier des X spécifié dans externXName avec des données lues à utiliser telles quelles
        ExternXDataTime, // utilisation du fichier des X spécifié dans externXName de type time_t seconds = time (NULL);
        spare1, // not used
        PrivateXData, // utilisation du fichier des X de meme nom que le fichier des Y avec des données lues à utiliser telles quelles
        PrivateXDataTime, // utilisation du fichier des X de meme nom que le fichier des Y avec des données de type time_t seconds = time (NULL);
        spare2, // not used
        OnePlotPerElement, // l'element sauvegardé ne se lit pas dans le temps, mais comme un plot complet ex : raw signal, spectre ....
        AutoXDataTime // génération auto du fichier des X de meme nom que le fichier des Y avec des données de type time_t seconds = time (NULL);
    };

    enum DataType {
        Char ,
        Short ,
        Int ,
        Long ,
        UChar,
        UShort ,
        UInt ,
        ULong,
        Float ,
        Double ,
        Custom
    };

    TSingleHkBackup(QString name,QString realName,DataType type, quint32 dataSize, QString unit,BackupOptions options, quint32 maxFileSize, QString externXName);
    ~TSingleHkBackup();

    void startNewSession(QString directory);
    void closeCurrentSession();
    void saveDescription(QSettings *settings);
    void flush();

    template <typename T>
    int addData(T*      data, int nbItemsToSave);
    template <typename T>
    int addDataXY(double* dataX, T*     dataY, int nbItemsToSave);
    qulonglong currentFilesSize();

    static void startMultipleSaveWithSameDatation(double datationInMs);
    static void stopMultipleSaveWithSameDatation();


private :

    void generateAndAddTime(int nbItemsToSave);
    inline void checkFileSizeAndOpenNewIfNeeded();
    void openNewFiles();
    int addDataX(double*    data, int nbItemsToSave);
    qulonglong m_currentFileSize;
    qulonglong m_currentXFileSize;
    qulonglong m_totalFilesSize;

//    FILE *m_fd;
//    FILE *m_fdX;
    QFile m_file;
    QFile m_fileX;
    bool m_sessionOpened;

    QString m_name;
    QString m_realName;
    BackupOptions m_options;
    quint32 m_maxFileSize;
    QString m_externXName;
    QString m_unit;
    QString m_directory;
    int m_fileNumber;
    DataType m_type;
    quint32 m_dataSize;
    quint32 m_dataSizeWritten;
    bool m_autoGenerateTimeLine;
    static bool m_useMultipleDatation;
    static double m_multipleDatation;
};

class THKBackup : public TSingleBackup
{
public:
    THKBackup(TAbstractParamsComputer *tfComputer);
    virtual ~THKBackup();

    /*******/
    /* addHK
        quint32 Id : ID du parametre (dans la liste des ID de TParametersTable
        quint32 DataType : type de l'element de base de la donnée
        quint32 valuesPerX : nombre de valeurs a lire pour une valeur de X du fichier temps (exemple mettre 180 pour sauver des raw signaux de 180 echantillons par periode)
        QString name : nom dispatcher (sera utilisé pour le nom du fichier
        QString realName : nom "humain" du parametre (sera utilisé dans la visu d'un graphe)
        QString unit : unité des valeurs (°, V, µA.....)
        TSingleBackup::BackupOptions flags : options de sauvegarde
        QString externXName : nom du fichier de donnée axe des X dans le cas ou il est "externe"
        quint32 maxFileSize : taille max d'un fichier, le decoupage des fichiers est automatique une fois cette taille atteinte
     */

    void addHK(quint32 Id,
               TSingleHkBackup::DataType type,
               quint32 valuesPerX,
               QString name,
               QString realName,
               QString unit,
               TSingleHkBackup::BackupOptions flags = TSingleHkBackup::AutoXDataTime,
               QString externXName = "",
               quint32 maxFileSize = defaultFileSize);

    void addHKFromDescription(TAbstractParametersTable *parametersTable, quint32 parameterId,
                              TSingleHkBackup::BackupOptions flags = TSingleHkBackup::AutoXDataTime,
                              QString externXName = "",
                              quint32 maxFileSize = defaultFileSize);
    void addHKFromDescription(TAbstractParametersTable *parametersTable, quint32 parameterId,
                              TSingleHkBackup::DataType forceDatatype,
                              TSingleHkBackup::BackupOptions flags = TSingleHkBackup::AutoXDataTime,
                              QString externXName = "",
                              quint32 maxFileSize = defaultFileSize);

    void addMultipleHKFromDescription(TAbstractParametersTable *parametersTable, QList<quint32> idList,
                                      TSingleHkBackup::BackupOptions flags = TSingleHkBackup::AutoXDataTime,
                                      QString externXName = "",
                                      quint32 maxFileSize = defaultFileSize);

    void addMultipleHKFromDescription(TAbstractParametersTable* parametersTable,QList<quint32> idList,
                                      TSingleHkBackup::DataType forceDatatype,
                                      TSingleHkBackup::BackupOptions flags = TSingleHkBackup::AutoXDataTime,
                                      QString externXName = "",
                                      quint32 maxFileSize = defaultFileSize);

    void deleteHK(quint32 Id);
    void clearHKList();

    /*forcer a sauver dans un repertoire donné en entrée*/
    bool startNewSession(QString backupDirectory
                                       , QString sessionName, QString comment);

    /* Dans le mode AutoXDataTime(Ms) si on veut sauver plusieurs parametres avec la meme date,
      entourer la sauvegarde des 2 fonctions suivantes :
      */
    void startMultipleSaveWithSameDatation(double datationInMs = -1);
    void stopMultipleSaveWithSameDatation();

    void flush();
    void closeCurrentSession();
    qulonglong sessionFileSize();

    void saveData(quint32 Id,char*     data, int nbItemsToSave);
    void saveData(quint32 Id,short*    data, int nbItemsToSave);
    void saveData(quint32 Id,int*      data, int nbItemsToSave);
    void saveData(quint32 Id,double*   data, int nbItemsToSave);
    void saveData(quint32 Id,unsigned char*     data, int nbItemsToSave);
    void saveData(quint32 Id,unsigned short*    data, int nbItemsToSave);
    void saveData(quint32 Id,quint32*      data, int nbItemsToSave);
    void saveData(quint32 Id,float*   data, int nbItemsToSave);

    void saveDataXY(quint32 Id,double* dataX, char*     dataY, int nbItemsToSave);
    void saveDataXY(quint32 Id,double* dataX, short*    dataY, int nbItemsToSave);
    void saveDataXY(quint32 Id,double* dataX, int*      dataY, int nbItemsToSave);
    void saveDataXY(quint32 Id,double* dataX, double*   dataY, int nbItemsToSave);
    void saveDataXY(quint32 Id,double* dataX, unsigned char*     dataY, int nbItemsToSave);
    void saveDataXY(quint32 Id,double* dataX, unsigned short*    dataY, int nbItemsToSave);
    void saveDataXY(quint32 Id,double* dataX, quint32* dataY, int nbItemsToSave);
    void saveDataXY(quint32 Id,double* dataX, float*   dataY, int nbItemsToSave);

    void savePartialInformation();
private :

    TSingleHkBackup::DataType getDataTypeFromParametersCodage(int parameterCodage);
    QHash<quint32, TSingleHkBackup *> hashBackupTable;
    int m_sessionId;
    TAbstractParamsComputer* m_tfComputer;
    QSettings *m_hkbSettings;

};

#endif // THKBACKUP_H
