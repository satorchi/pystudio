//File generated by Dispatcher wizard v 2.9.3.0.1 (23/08/2018) .
//Generating date : lun. janv. 28 18:13:28 2019

//---------------------------------------------------------------------------
#ifndef TTELEMETRYDECODE_H
#define TTELEMETRYDECODE_H
//---------------------------------------------------------------------------

#include "tparameters.h"
#include <QHash>
#include <QtEndian>

class TVirtualDecommutation;

class TTelemetryDecode
{
public:
    TTelemetryDecode(TVirtualDecommutation* decommutation,TParameters* Parameters);
    QHash<quint64, QList<quint32>* > decodedParametersPerTelemetry; /**< list of parameters per telemetry.*/
/** \@brief Decode the EXT_TM1 telemetry.
 *
 * Decode the 8 bits EXT_TM1 telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry EXT_TM1 telemetry buffer.
 */
	void decodeEXTERN_HKS_EXT_TM1(quint8* telemetry);
/** \@brief Decode the QUBIC_HK telemetry.
 *
 * Decode the 8 bits QUBIC_HK telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry QUBIC_HK telemetry buffer.
 */
	void decodeMULTINETQUICMANAGER_QUBIC_HK(quint8* telemetry);
/** \@brief Decode the QUBIC_SUM telemetry.
 *
 * Decode the 8 bits QUBIC_SUM telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry QUBIC_SUM telemetry buffer.
 */
	void decodeMULTINETQUICMANAGER_QUBIC_SUM(quint8* telemetry);
/** \@brief Decode the QUBIC_RAW telemetry.
 *
 * Decode the 8 bits QUBIC_RAW telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry QUBIC_RAW telemetry buffer.
 */
	void decodeMULTINETQUICMANAGER_QUBIC_RAW(quint8* telemetry);
/** \@brief Decode the CFIBERS telemetry.
 *
 * Decode the 8 bits CFIBERS telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry CFIBERS telemetry buffer.
 */
	void decodeCFIBERS_CFIBERS(quint8*);
/** \@brief Decode the RFSWITCHES telemetry.
 *
 * Decode the 8 bits RFSWITCHES telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry RFSWITCHES telemetry buffer.
 */
	void decodeRFSWITCHES_RFSWITCHES(quint8*);
/** \@brief Decode the MMR3 telemetry.
 *
 * Decode the 8 bits MMR3 telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry MMR3 telemetry buffer.
 */
	void decodeMMR3_MMR3(quint8*);
/** \@brief Decode the MGC3 telemetry.
 *
 * Decode the 8 bits MGC3 telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry MGC3 telemetry buffer.
 */
	void decodeMGC3_MGC3(quint8*);
/** \@brief Decode the HWP_ACK telemetry.
 *
 * Decode the 8 bits HWP_ACK telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry HWP_ACK telemetry buffer.
 */
	void decodeHWP_HWP_ACK(quint8*);
/** \@brief Decode the HWP_DATA telemetry.
 *
 * Decode the 8 bits HWP_DATA telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry HWP_DATA telemetry buffer.
 */
	void decodeHWP_HWP_DATA(quint8*);
/** \@brief Decode the CALIBSRCTM telemetry.
 *
 * Decode the 8 bits CALIBSRCTM telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry CALIBSRCTM telemetry buffer.
 */
	void decodeCALIBSOURCES_CALIBSRCTM(quint8* telemetry);
/** \@brief Decode the PLATFORMCONTROLERTM telemetry.
 *
 * Decode the 8 bits PLATFORMCONTROLERTM telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry PLATFORMCONTROLERTM telemetry buffer.
 */
	void decodePLATFORMCONTROLER_PLATFORMCONTROLERTM(quint8* telemetry);
/** \@brief Decode the PLATFORMAZMOTORTM telemetry.
 *
 * Decode the 8 bits PLATFORMAZMOTORTM telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry PLATFORMAZMOTORTM telemetry buffer.
 */
	void decodePLATFORMMOTORS_PLATFORMAZMOTORTM(quint8*);
/** \@brief Decode the PLATFORMELMOTORTM telemetry.
 *
 * Decode the 8 bits PLATFORMELMOTORTM telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry PLATFORMELMOTORTM telemetry buffer.
 */
	void decodePLATFORMMOTORS_PLATFORMELMOTORTM(quint8*);
/** \@brief Decode the GPSTM telemetry.
 *
 * Decode the 8 bits GPSTM telemetry buffer and update the TParameters instance.
 * \@param [in] telemetry GPSTM telemetry buffer.
 */
	void decodeGPS_GPSTM(quint8*);

    protected:
        TParameters* _parameters;
        TVirtualDecommutation* _Decommutation;
    };
    
#endif // TTELEMETRYDECODE_H    