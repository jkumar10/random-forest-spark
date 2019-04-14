from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import StringIndexer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import sys

# filename = 'file:///N/u/jaikumar/data/'+str(sys.argv[1])
filename='file:///N/u/jaikumar/data/2006.csv'

# Creating a spark session and giving a name to the application as "RF_air".
# getorCreate() is a method that is used to create the spark session.
spark=SparkSession.builder.appName('RF_air').getOrCreate()

# Here we are loading the data from the file which is stored in the variable filename
# inferschema will define the schema of the data and header will give lable each column
# data.printSchema() will return all the features i.e. all the column labels in the data.
data = spark.read.csv(filename,inferSchema=True,header=True)

# drop() method will delete all the rows containing Null or NaN values
df1=data.drop()

# Here training data is created by adding an extra label or column "isDelay" with entry Yes or No
# according to the value of DepDelay column. DepDelay column is only considered for training or 
# labeling the data. While testing the algorithm DepDelay will not be passed.
df2=df1.withColumn('isDelay',when(df1.DepDelay <= 0,'No').otherwise('Yes'))

# Here we are passing the feature columns into vector assembler that we will use for classification.
# output column is defined as "features"
assembler = VectorAssembler(
  inputCols=['Year',
             'Month',
             'DayofMonth',
             'DayOfWeek',
             'DepTime',
             'CRSDepTime',
             'ArrTime',
             'CRSArrTime',
             'FlightNum',
             'ActualElapsedTime',
             'CRSElapsedTime',
             'AirTime',
             'ArrDelay',
             'Distance',
             'TaxiIn',
             'TaxiOut',
             'CarrierDelay',
            'WeatherDelay',
            'SecurityDelay',
            '0SDelay',
            'LateAircraftDelay'],
              outputCol="features")

output = assembler.transform(df2)

# Spark's mllib directly cannot deal with "Yes" or "No" values so we used StringIndexer method.
# isDelayIndex is created after transforming string values to O and 1.
indexer = StringIndexer(inputCol="isDelay", outputCol="isDelayIndex")

output_fixed = indexer.fit(output).transform(output)

final_data = output_fixed.select("features",'isDelayIndex')

train_data,test_data = final_data.randomSplit([0.3,0.7])

rfc = RandomForestClassifier(labelCol='isDelayIndex',featuresCol='features')

rfc_model = rfc.fit(train_data)

rfc_predictions = rfc_model.transform(test_data)

acc_evaluator = MulticlassClassificationEvaluator(labelCol="isDelayIndex", predictionCol="prediction", metricName="accuracy")

rfc_acc = acc_evaluator.evaluate(rfc_predictions)

print("Here are the results!")

print('A random forest ensemble had an accuracy of: {0:2.2f}%'.format(rfc_acc*100))


