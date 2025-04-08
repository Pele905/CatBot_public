import numpy as np 
import matplotlib.pyplot as plt 

# Data is set up like this "Syringe 1" : {'Steps: {300}}
pump_data = {'Pump 1': {'300 steps': [992, 978, 999],'600 steps': [2000, 2012, 1986], '900 steps': [2954, 3012, 2949], '4500 steps': [14881, 14928, 14897]},
                'Pump 2': {'300 steps': [1012, 1005, 1013], '900 steps': [2982, 2997, 2993], '4500 steps': [14886]},
                'Pump 3': {'300 steps': [508, 508, 505], '900 steps': [1516, 1504, 1503], '4500 steps': [7505, 7528, 7456]},
                'Pump 4': {'300 steps': [990, 974, 1005], '900 steps': [3002, 2995, 2945], '4500 steps': [14871, 14917, 14911]},
                'Pump 5': {'300 steps': [996, 990, 989],'600 steps': [1984, 1976, 1981], '900 steps': [2998, 2899], '4500 steps': [14878, 14908]},
                'Pump 6': {'300 steps': [1001, 1002, 994], '900 steps': [2983,2962,2988], '4500 steps': [14829, 14909, 14883]},
                'Pump 7': {'300 steps': [999, 976, 992], '900 steps': [2962, 2966,2953], '4500 steps': [14806, 14986]}}

# How many steps per ml 
pump_data_calibration = {'Pump 1' : 302, "Pump 2" : 303, 
                         "Pump 3" : 601, "Pump 4" : 302, 
                         "Pump 5": 302, "Pump 6": 303,
                         "Pump 7": 302
}
for pump_i in pump_data:

    plt.figure(figsize = (14, 9))

    data_300 = pump_data[pump_i]['300 steps']
    data_900 = pump_data[pump_i]['900 steps']
    data_4500 = pump_data[pump_i]['4500 steps']

    if data_300 == []:
        continue
    
    fit_vec_x = len(data_300) * [300] + len(data_900) * [900] + len(data_4500) * [4500]
    fit_vec_y = data_300 + data_900 + data_4500
    plt.scatter(len(data_300) * [300], data_300)
    plt.scatter(len(data_900) * [900],data_900)
    plt.scatter(len(data_4500) * [4500], data_4500)

    plt.errorbar(len(data_300) * [300], data_300,yerr=np.std(data_300))
    plt.errorbar(len(data_900) * [900], data_900,yerr=np.std(data_900))
    plt.errorbar(len(data_4500) * [4500], data_4500,yerr=np.std(data_4500))

    #print("Std 300:", np.std(data_300),"300 Error in %:", 100 * np.std(data_300) / np.mean(data_300))
    #print("Std 900:", np.std(data_900),"900 Error in %:", 100 * np.std(data_900) / np.mean(data_900))
    #print("Std 4500:", np.std(data_4500),"4500 Error in %:", 100 * np.std(data_4500) / np.mean(data_4500))

    std_300 = np.std(data_300)
    std_900 = np.std(data_900)
    std_4500 = np.std(data_4500)

    plt.text(300, np.mean(data_300) + std_300 - 1300, f'error = {100 * std_300 / np.mean(data_300):.2f}%', ha='center',
             fontsize = 20)
    plt.text(900, np.mean(data_900) + std_900 - 1300, f'error = {100 * std_900 / np.mean(data_900):.2f}%', ha='center',
             fontsize = 20)
    plt.text(4500, np.mean(data_4500) + std_4500 - 1300, f'error = {100 * std_4500 / np.mean(data_4500):.2f}%',
              ha='center', fontsize  = 20)

    b, a = np.polyfit(fit_vec_x,fit_vec_y, deg = 1)

    plt.plot(np.linspace(300, 4500, 100), b * np.linspace(300, 4500, 100) + a)

    plt.xlabel("Steps", fontsize = 20)
    plt.ylabel("Weight [mg]",fontsize = 20)
    plt.xticks(fontsize = 20)
    plt.yticks(fontsize = 20)
    plt.title(f"Syringe {pump_i}", fontsize = 20)
    plt.tight_layout()
    #plt.savefig(f"Syringe_pump_calibration_curves/Calibration_{pump_i}.png")
    print(np.round(1000 / b))
    #plt.show()

