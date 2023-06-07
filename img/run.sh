#!/bin/zsh

python3 ./bin2img.py calibration_hue_blue_100m_32.CUBE.rgb.bin 1024 32 clbhbm32.png
python3 ./bin2img.py calibration_hue_blue_100p_32.CUBE.rgb.bin 1024 32 clbhbp32.png
python3 ./bin2img.py calibration_hue_green_100m_32.CUBE.rgb.bin 1024 32 clbhgm32.png
python3 ./bin2img.py calibration_hue_green_100p_32.CUBE.rgb.bin 1024 32 clbhgp32.png
python3 ./bin2img.py calibration_hue_red_100m_32.CUBE.rgb.bin 1024 32 clbhrm32.png
python3 ./bin2img.py calibration_hue_red_100p_32.CUBE.rgb.bin 1024 32 clbhrp32.png
python3 ./bin2img.py calibration_sat_blue_100m_32.CUBE.rgb.bin 1024 32 clbsbm32.png
python3 ./bin2img.py calibration_sat_blue_100p_32.CUBE.rgb.bin 1024 32 clbsbp32.png
python3 ./bin2img.py calibration_sat_green_100m_32.CUBE.rgb.bin 1024 32 clbsgm32.png
python3 ./bin2img.py calibration_sat_green_100p_32.CUBE.rgb.bin 1024 32 clbsgp32.png
python3 ./bin2img.py calibration_sat_red_100m_32.CUBE.rgb.bin 1024 32 clbsrm32.png
python3 ./bin2img.py calibration_sat_red_100p_32.CUBE.rgb.bin 1024 32 clbsrp32.png

python3 ./bin2img.py a2b.CUBE.rgb.bin 1024 32 clba2b.png
python3 ./bin2img.py b2a.CUBE.rgb.bin 1024 32 clbb2a.png
