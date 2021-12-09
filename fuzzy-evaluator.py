import matplotlib.pyplot as plt
from matplotlib.pyplot import plot
import pprint as pp
import xlrd
import math

dataset = []
controlData = []
testData = []

import csv

with open('input_data.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        print(row)
        dataset.append(row)
        line_count += 1

# thresshold

mid = 85
low = 60

interval = 10


def dist(a, b):
    return b - a


def sigmoidUp(x, a, b):
    if x <= a:
        return 0
    elif x <= a + dist(a, b) / 2:
        return 2 * math.pow((x - a) / (b - a), 2)
    elif x < b:
        return 1 - (2 * math.pow((b - x) / (b - a), 2))
    else:
        return 1


def sigmoidDown(x, a, b):
    if x <= a:
        return 1
    elif x <= a + dist(a, b) / 2:
        return 1 - (2 * math.pow((x - a) / (b - a), 2))
    elif x < b:
        return 2 * math.pow((b - x) / (b - a), 2)
    else:
        return 0


def sigmoid(x, min, max):
    return sigmoidUp(x, min, min + (dist(min, max) / 2)) if (x < min + dist(min, max) / 2) else sigmoidDown(x, min + (
                dist(min, max) / 2), max)


def rendah(x):
    return sigmoidDown(x, 0, low + interval)


def sedang(x):
    return sigmoid(x, low - interval, mid + interval)


def tinggi(x):
    return sigmoidUp(x, mid - interval, 100)


def Fuzzification(crispData):
    return {
        'low': rendah(crispData),
        'mid': sedang(crispData),
        'high': tinggi(crispData)
    }


def Inteference(fuzzyData):
    return {
        'Y': (fuzzyData[0]['low'] and fuzzyData[1]['high'])
             or (fuzzyData[0]['high'] and fuzzyData[1]['low'])
             or (fuzzyData[0]['mid'] and fuzzyData[1]['mid'])
             or (fuzzyData[0]['high'] and fuzzyData[1]['mid'])
             or (fuzzyData[0]['high'] and fuzzyData[1]['high'])
             or (fuzzyData[0]['mid'] and fuzzyData[1]['high']),
        'N': (fuzzyData[0]['low'] and fuzzyData[1]['low'])
             or (fuzzyData[0]['low'] and fuzzyData[1]['mid'])
             or (fuzzyData[0]['mid'] and fuzzyData[1]['low'])
    }


def Defuzzification(fuzzyData):
    return ((fuzzyData['Y'] * 70) + (fuzzyData['N'] * 30)) // (fuzzyData['Y'] + fuzzyData['N'])


def evalData(dataset):
    fuzzyData = []
    for data in dataset:
        fuzzyData.append([Fuzzification(data['writtenScore']), Fuzzification(data['InterviewScore'])])
    print('Fuzzy data values : ')
    pp.pprint(fuzzyData)

    InterData = []
    for data in fuzzyData:
        InterData.append(Inteference(data))
    print('\nInteference data values : ')
    pp.pprint(InterData)

    res = []
    # output result from the defuzzifier
    for data in InterData:
        res.append(Defuzzification(data))  # append the evaluated result to the og list
    print('\nResult : ')
    print(res)
    print('\n==============Final Competency Evaluation==================')
    return ['Y' if (math.floor(x) >= 50.0) else 'N' for x in res]


if __name__ == '__main__':
    # initialize control dataset
    for i in range(0, len(dataset)):
        controlData.append({
            'id': i + 1,
            'writtenScore': float(dataset[i]["Written Score"]),
            'InterviewScore': float(dataset[i]["Interview Score"]),
            'result': "Y" if int(dataset[i]["Recommend Score"]) == 1 else "N"
        })
    print(len(controlData))
    testData = controlData[20:]
    controlData = controlData[:20]

    print('control dataset : ')
    pp.pprint(controlData)

    print('\ntest dateset : ')
    pp.pprint(testData)
    print()

    accuracy = 0
    result = evalData(controlData)
    for i in range(0, len(result)):
        if (result[i] == controlData[i]['result']):
            accuracy += 1

    print(result)
    print([x['result'] for x in controlData])
    print('\naccuracy ' + str((accuracy / 18) * 100))

    result = evalData(testData)
    print("\ntest data result: ")
    print(result)
    with open('output_data.csv', mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=",", quotechar='\"', quoting=csv.QUOTE_MINIMAL)
        for r in result:
            output_writer.writerow(["`YES" if r == "Y" else "NO"])

    # graph fuzzy membership values
    plt.xlabel('crisp data values(x)')
    plt.ylabel('fuzzy output')
    plt.title('')
    plt.plot([x for x in range(0, low + interval)],
             [sigmoidDown(x, 0, low + interval) for x in range(0, low + interval)])
    plt.plot([x for x in range(low - interval, mid + interval)], [sigmoid(x, low - interval, mid + interval) for x in
                                                                  range(low - interval,
                                                                        mid + interval)])  # sigmoid from low-interval to mid+interval
    plt.plot([x for x in range(mid - interval, 100)],
             [sigmoidUp(x, mid - interval, 100) for x in range(mid - interval, 100)])
    plt.show()
