from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType, TimestampType, LongType
import databrickslabs_testdatagenerator as datagen
from pyspark.sql import SparkSession
import unittest
from datetime import timedelta, datetime
from databrickslabs_testdatagenerator import DateRange, NRange

# build spark session

# global spark

spark = datagen.SparkSingleton.getLocalInstance("unit tests")


class TestDependentData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.country_codes=['CN', 'US', 'FR', 'CA', 'IN', 'JM', 'IE', 'PK', 'GB', 'IL', 'AU', 'SG', 'ES', 'GE', 'MX', 'ET', 'SA', 'LB', 'NL']
        cls.country_weights=[1300, 365, 67, 38, 1300, 3, 7, 212, 67, 9, 25, 6, 47, 83, 126, 109, 58, 8, 17]

        cls.manufacturers = ['Delta corp', 'Xyzzy inc', 'Lakehouse Ltd', 'Parquet LLC', 'Ipsum Lorem Devices']

        cls.lines = ['delta', 'xyzzy', 'lakehouse', 'parquet', 'ipsum']
        cls.line_weights= [10, 5, 5, 5, 5]

        cls.rows = 1000000
        cls.devices=100


        cls.testDataSpec = (datagen.DataGenerator(sparkSession=spark, name="device_data_set", rows=cls.rows,
                                                  partitions=4, seed_method='hash_fieldname', debug=False, verbose=False)
                            .withIdOutput()
                            # we'll use hash of the base field to generate the ids to avoid a simple incrementing sequence
                            .withColumn("internal_device_id", LongType(), min=0x1000000000000, unique_values=cls.devices)

                            # note for format strings, we must use "%lx" not "%x" as the underlying value is a long
                            .withColumn("device_id", StringType(), expr="format_string('0x%013x', internal_device_id)", base_column="internal_device_id")
                            #.withColumn("device_id", StringType(), format='0x%013x', base_column="internal_device_id")

                            # the device / user attributes will be the same for the same device id - so lets use the internal device id as the base column for these attribute
                            .withColumn("country", StringType(), values=cls.country_codes, weights=cls.country_weights, base_column="internal_device_id")
                            .withColumn("manufacturer", StringType(), values=cls.manufacturers, base_column="internal_device_id")
                            .withColumn("line", StringType(), values=cls.lines, base_column="manufacturer", base_column_type="hash")
                            .withColumn("line2", StringType(), values=cls.lines, weights=cls.line_weights, base_column="manufacturer", base_column_type="hash")
                            .withColumn("model_ser", IntegerType(), min=1, max=11,  base_column="device_id", base_column_type="hash")
                            .withColumn("model_ser2", IntegerType(), unique_values=11,  base_column="device_id", base_column_type="hash")
                            .withColumn("model_ser3", IntegerType(), data_range=NRange(1, 11, 1),  base_column="internal_device_id")
                            .withColumn("model_ser4", IntegerType(), data_range=NRange(1, 11, 1), base_column="device_id",
                                         base_column_type="hash")
                            .withColumn("model_ser5", IntegerType(), data_range=NRange(1, 11),
                                         base_column="device_id",
                                         base_column_type="hash")

                            )

        cls.dfTestData = cls.testDataSpec.build()

    def test_setup(self):
        self.assertIsNotNone(self.dfTestData)
        self.assertIsNotNone(self.testDataSpec)
        self.assertEqual(self.rows, self.dfTestData.count())

    def test_dependent_string_fields1(self):
        self.assertEqual(0, self.dfTestData.where("model_ser is  null").count(), "should not have null values")
        self.assertGreater( self.dfTestData.where("model_ser == 1").count(), 0,  "should have values with 1")
        self.assertGreater(self.dfTestData.where("model_ser == 11").count(), 0, "should have values with 11")
        self.assertEqual(0, self.dfTestData.where("model_ser < 1").count(), "should not values < 1")
        self.assertEqual(0, self.dfTestData.where("model_ser > 11").count(), "should not values > 11")

    def test_dependent_string_fields2(self):
        self.assertEqual(0, self.dfTestData.where("model_ser2 is  null").count(), "should not have null values")
        self.assertGreater( self.dfTestData.where("model_ser2 == 1").count(), 0,  "should have values with 1")
        self.assertGreater(self.dfTestData.where("model_ser2 == 11").count(), 0, "should have values with 11")
        self.assertEqual(0, self.dfTestData.where("model_ser2 < 1").count(), "should not values < 1")
        self.assertEqual(0, self.dfTestData.where("model_ser2 > 11").count(), "should not values > 11")

    def test_dependent_string_fields3(self):
        self.dfTestData.where("model_ser3 < 1 or model_ser3 > 11" ).show()
        self.assertEqual(0, self.dfTestData.where("model_ser3 is  null").count(), "should not have null values")
        self.assertGreater( self.dfTestData.where("model_ser3 == 1").count(), 0, "should have values with 1")
        self.assertGreater(self.dfTestData.where("model_ser3 == 11").count(), 0, "should have values with 11")
        self.assertEqual(0, self.dfTestData.where("model_ser3 < 1").count(), "should not values < 1")
        self.assertEqual(0, self.dfTestData.where("model_ser3 > 11").count(), "should not values > 11")

    def test_dependent_string_fields4(self):
        self.dfTestData.where("model_ser4 < 1 or model_ser4 > 11" ).show()
        self.assertEqual(0, self.dfTestData.where("model_ser4 is  null").count(), "should not have null values")
        self.assertGreater( self.dfTestData.where("model_ser4 == 1").count(), 0, "should have values with 1")
        self.assertGreater(self.dfTestData.where("model_ser4 == 11").count(), 0, "should have values with 11")
        self.assertEqual(0, self.dfTestData.where("model_ser4 < 1").count(), "should not values < 1")
        self.assertEqual(0, self.dfTestData.where("model_ser4 > 11").count(), "should not values > 11")

    def test_dependent_string_fields5(self):
        self.dfTestData.where("model_ser5 < 1 or model_ser5 > 11" ).show()
        self.assertEqual(0, self.dfTestData.where("model_ser5 is  null").count(), "should not have null values")
        self.assertGreater( self.dfTestData.where("model_ser5 == 1").count(), 0, "should have values with 1")
        self.assertGreater(self.dfTestData.where("model_ser5 == 11").count(), 0, "should have values with 11")
        self.assertEqual(0, self.dfTestData.where("model_ser5 < 1").count(), "should not values < 1")
        self.assertEqual(0, self.dfTestData.where("model_ser5 > 11").count(), "should not values > 11")

    def test_dependent_line(self):
        self.dfTestData.where("line is  null").show()
        self.assertEqual(0, self.dfTestData.where("line is  null").count(), "should not have null values")

    def test_dependent_line1(self):
        # for given manufacturer, should have the same line
        self.dfTestData.createOrReplaceTempView("test_data2")

        df2 = spark.sql("select count(distinct line) as c, manufacturer from test_data2 group by manufacturer")
        df2.show()

        self.assertEqual(0, df2.where("c > 1").count(), "should not more than one value for line for same manufacturer ")

    def test_dependent_line2(self):
        self.assertEqual(0, self.dfTestData.where("line2 is  null").count(), "should not have null values")
        # for given manufacturer, should have the same line
        self.dfTestData.createOrReplaceTempView("test_data3")

        df2 = spark.sql("select count(distinct line2) as c, manufacturer from test_data3 group by manufacturer")
        df2.show()

        self.assertEqual(0, df2.where("c > 1").count(), "should not more than one value for line for same manufacturer ")

    def test_dependent_country(self):
        self.assertEqual(0, self.dfTestData.where("country is  null").count(), "should not have null values")

        # for given device id, should have the same country
        self.dfTestData.createOrReplaceTempView("test_data")

        df2 = spark.sql("select count(distinct country) as c from test_data group by device_id")
        self.assertEqual(0, df2.where("c > 1").count(), "should not more than one value for country for same device id ")


    def test_format_dependent_data(self):
        ds_copy1 = self.testDataSpec.clone()

        df_copy1 = (ds_copy1.setRowCount(1000)
                    .withColumn("device_id_2", StringType(), format='0x%013x', base_column="internal_device_id")
                    .build())

        df_copy1.show()