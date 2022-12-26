# Pressure Evaluation
Scripts to evaluate and process pressure data from multi-hole probes, pressure rakes and pitot tubes

![alt text](https://github.com/hohenhau/pressure_evaluatio/blob/main/_process_diagram.png?raw=true)

## 1. Analysis of Multi-Hole Probe Pressures

Multi-Hole Probes are essentially [Pitot Tubes](https://en.wikipedia.org/wiki/Pitot_tube) with multiple pressure ports. While a Pitot Tube can only estimate the velocity magnitude, the differences in pressure between the ports of a [Multi-Hole Probe](https://www.surreysensors.com/products/digital-seven-hole-probe-system/) allow for the estimation all three velocity components. The script herein is suitable for probes with 5 holes or more.

### 1.1 Multi-Hole Probe Calibration and Interpolation

Usually, Multi-Hole probes are supplied with calibration files. These contain measurements take at a range of different yaw and pitch angles. The incriments of the angles are usually too coarse to be used in experiments. It is therefore necessary to use interpolation to artificially increase the resolution and thereby the accuracy of the probe. This interpolation is carried out with the [run_interpolate.py](https://github.com/hohenhau/pressure_evaluation/blob/main/run_interpolate.py) script.

### 1.2 Estimating Velocity Components from Multi-Hole Probe Data

### 1.3 Sorting Velocity Components into Distinct Time Frames

### 1.4 Assigning Velocity Components to Specific Coordinates

## 2. Analysis of Pito Rake Pressures

### 2.1 Estimating Velocity Magnitudes from Pitot Rakes

### 2.2 Assigning Velocity Magnitudes to Specific Coordinates

## 3. Analysis of Pitot Static Tube Pressures

### 3.1 Sorting Static Pressures into Distinct Time Frames
