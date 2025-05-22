import time
import board
import adafruit_veml7700

i2cl = board.I2C()

veml7700 = adafruit_veml7700.VEML7700(i2cl)

veml7700.light_gain = veml7700.ALS_GAIN_1
veml7700.light_integration_time = veml7700.ALS_100MS

def computeLux(lux, corrected):
    if corrected:
        # return (((6.0135e-13 * lux - 9.3924e-9) * lux + 8.1488e-5) * lux + 1.0023) * lux
        return (6.0135e-13 * lux ** 4) + (-9.3924e-9 * lux ** 3) + (8.1488e-5 * lux ** 2) + (1.0023 * lux)
      
    return lux
  
def autoLux():
    gains = list(veml7700.gain_values.keys())
    intTimes = list(veml7700.integration_time_values.keys())

    gainIndex = gains.index(veml7700.light_gain)
    itIndex = intTimes.index(veml7700.light_integration_time)
    useCorrection = False

    ALS = veml7700.light

    if ALS <= 100:

        """increase first gain and then integration time as needed
        compute lux using simple linear formula"""
        while ALS <= 100 and (gainIndex < 3 or itIndex < 5):
            print("gainIndex, itIndex:", gainIndex, itIndex)

            if gainIndex < 3:
                gainIndex += 1
                veml7700.light_gain = gains[gainIndex]
                #print("Increasing gain to", veml7700.light_gain)
            elif itIndex < 5:
                itIndex += 1
                veml7700.light_integration_time = intTimes[itIndex]
                #print("Increasing integration time to", veml7700.light_integration_time)

    else:
        """decrease integration time as needed
        compute lux using non-linear correction"""
        useCorrection = True
        while (ALS > 10000) and (itIndex > 0):
            itIndex -= 1
            veml7700.light_integration_time = intTimes[itIndex]
            #print("Lowering integration time to", veml7700.light_integration_time)

    #print("Gain, it: ", veml7700.light_gain, veml7700.light_integration_time)

    if useCorrection:
        adjustedLux = computeLux(veml7700.lux, True)
        #print("Lux (standard, corrected, raw):", veml7700.lux, adjustedLux, ALS)
        lux_level = adjustedLux
        return lux_level
        #return adjustedLux
    else:
        #print("Lux (standard, raw):", veml7700.lux, ALS)
        lux_level = veml7700.lux
        #return veml7700.lux
        return lux_level


#while True:
#    autoLux()
#    """print(veml7700.lux, veml7700.light)"""
#    time.sleep(1)
