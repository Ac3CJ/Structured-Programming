# EE20084 - Structured Programming: Cascade Circuit V/I Characteristics Analyzer

## Overview
This program is designed to read and analyze the output Voltage/Current (V/I) characteristics of a cascade circuit containing series and parallel passive components: Resistors, Capacitors, and Inductors. The program performs an analysis of the circuit's behavior over a frequency sweep and presents the data in various formats, including Scientific Notation, SI Prefixes, and Decibels.

## Features
- **Frequency Sweep Analysis**: The program simulates the circuit's response over a range of frequencies.
- **Data Output Formats**: 
  - Scientific Notation
  - SI Prefixes (e.g., m, k, M, etc.)
  - Decibels (dB)
- **Component Support**: The program supports common passive components such as:
  - Resistors (R)
  - Capacitors (C)
  - Inductors (L)
- **Customizable Circuit Configuration**: Users can define series or parallel configurations of components within the cascade circuit.
  
## Requirements
- Python 3.7 or higher
- Required Libraries:
  - `numpy` (for numerical operations)
  - `matplotlib` (for plotting)
  - `scipy` (for scientific computations)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/Ac3CJ/Structured-Programming.git
   ```

2. Navigate into the project directory:
   ```bash
   cd Structured-Programming
   ```

3. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
To run the program, simply execute the following command in your terminal:
```bash
python CascadeCircuit.py
```

### Input
The program prompts you to input the following parameters for the cascade circuit:
- Component values (Resistance, Capacitance, Inductance)
- Circuit configuration (series or parallel)
- Frequency range for the sweep
- Desired output format (Scientific Notation, SI Prefixes, or Decibels)

### Example
```bash
Enter component values:
- Resistor (R): 1000 ohms
- Capacitor (C): 10 µF
- Inductor (L): 1 H

Enter frequency range:
- Start Frequency: 10 Hz
- End Frequency: 10 kHz

Choose output format:
1. Scientific Notation
2. SI Prefixes
3. Decibels
```

### Output
The program will display or save the analysis results in the selected format, showing the V/I characteristics of the circuit over the frequency sweep.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- Dr. [Jonathan Graham-Harper-Cater](https://researchportal.bath.ac.uk/en/persons/jonathan-graham-harper-cater), University of Bath
- Dr. [Stephen Pennock](https://researchportal.bath.ac.uk/en/persons/stephen-pennock), University of Bath
