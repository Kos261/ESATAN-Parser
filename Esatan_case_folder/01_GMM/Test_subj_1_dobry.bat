
set     PFAD_GMM=C:\Users\koste\OneDrive\Pulpit\AT_ParserFiles\01_GMM\

rem call submodels

call C:\ESATAN-TMS\2018sp1\Radiative\bin\esrdg.bat < %PFAD_GMM%02_SUBMODELS\1_TCS_FPM_TVAC.erg > 	%PFAD%1_TCS_FPM_TVAC.out

call C:\ESATAN-TMS\2018sp1\Radiative\bin\esrdg.bat < %PFAD_GMM%Test_subj_1.erg >			%PFAD%99_Test_all.out

pause


::call C:\ESATAN-TMS\2018sp1\Radiative\bin\esrdg.bat < %PFAD_GMM%02_SUBMODELS\1_FCU_HA_v03.erg > 	%PFAD%1_FCU_HA_v03.out
::call C:\ESATAN-TMS\2018sp1\Radiative\bin\esrdg.bat < %PFAD_GMM%02_SUBMODELS\2_FCU_PSU_v03.erg > %PFAD%2_FCU_PSU.out
::C:\ESATAN-TMS\2018sp1\Radiative\bin\esrdg.bat < %PFAD_GMM%02_SUBMODELS\2_FGS_TA_Rv04.erg > %PFAD%2_FGS_TA_Rv04.out
::call C:\ESATAN-TMS\2018sp1\Radiative\bin\esrdg.bat < %PFAD_GMM%02_SUBMODELS\8_EROS_DU_v01.erg > %PFAD%8_EROS_DU_v01.out

:: assemble model from module *.erg files