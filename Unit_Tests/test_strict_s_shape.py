import unittest
from Models.Strict_S_Shape import Strict_S_Shape
import numpy as np

# unit testing for the directional warehouse where backtracking across the top cross-aisle is allowed after the final pick if required

class Test_model(unittest.TestCase):

    def test_output_type(self):
        model_status_result, distance_result, time_result, assignment_result = Strict_S_Shape(num_aisles = 3, 
                                                                                              num_bays = 2, 
                                                                                              slot_capacity = 2, 
                                                                                              between_aisle_dist = 1, 
                                                                                              between_bay_dist = 1, 
                                                                                              orders = {1:[1,2,3], 2:[2,3,4], 3:[3,4,5]})
        
        self.assertIsInstance(model_status_result, int, msg = f"Model Status is the wrong variable type, is type {type(model_status_result)}, should be int") # confirm that the model status returns an integer (for optimal, infeasible, unbounded and so forth)

        self.assertIsInstance(distance_result, float, msg = f"Final distance is the wrong variable type, is type {type(distance_result)}, should be float.") # confirm that the final distance is a float

        self.assertIsInstance(time_result, float, msg = f"Time result is the wrong variable type, is type {type(time_result)}, should be float.") # confirm that the time taken for the model to run is a float

        self.assertIsInstance(assignment_result, dict, msg = f"Assignment list is the wrong variable type, is type {type(assignment_result)}, should be dictionary") # confirm that the list of assignments in indeed a list

        for assignment in assignment_result:
            self.assertIsInstance(assignment_result[assignment], int, msg = f"Individual assignments are the wrong variable type, is type {type(assignment)}, should be list") # confirm that each of the assignments is a tuple

    def test_instance_1(self): # feasible
        instance = [3, 2, 2, 1, 1, {1:[1,2,3], 2:[2,3,4], 3:{3,4,5}}]
        
        model_status_result, distance_result, time_result, assignment_result = Strict_S_Shape(instance[0],
                                                                                              instance[1],
                                                                                              instance[2],
                                                                                              instance[3],
                                                                                              instance[4],
                                                                                              instance[5])
        
        self.assertEqual(model_status_result, 2, msg= f"Model status is incorrect. It should be feasible (2), is returning {model_status_result}.")

        self.assertEqual(distance_result, 6*instance[3] + 6*(instance[4]*(instance[1] + 1)), msg = f"model is obtaining the wrong final distance. Minimum distance is {6*instance[3] + 6*(instance[4]*(instance[1] + 1))}. The model is achieving {distance_result}.")

    def test_instance_2(self): # feasible
        instance = [4, 3, 2, 1, 1, {1:[1,2,3,4,5,6], 2:[7,8,9,10,11,12], 3:[1,2,3,7,8,9], 4:[4,5,6,10,11,12], 5:[1,2,3,11,12,13]}]

        model_status_result, distance_result, _, _ = Strict_S_Shape(instance[0],
                                                                    instance[1],
                                                                    instance[2],
                                                                    instance[3],
                                                                    instance[4],
                                                                    instance[5])
        
        self.assertEqual(model_status_result, 2, msg= f"Model status is incorrect. It should be feasible (2), is returning ({model_status_result}).")

        self.assertEqual(distance_result, 54, msg = f"model is obtaining the wrong final distance. Minimum distance is {54}. The model is achieving {distance_result}.")

    def test_instance_3(self): # infeasible
        instance = [2, 2, 2, 1, 1, {1:[1,2,3,4], 2:[5,6,7,8], 3:[9,10,11,12]}]

        model_status_result, _, _, _ = Strict_S_Shape(instance[0],
                                                      instance[1],
                                                      instance[2],
                                                      instance[3],
                                                      instance[4],
                                                      instance[5])

        self.assertEqual(model_status_result, 3, msg = f"Model status is incorrect. It should be infeasible (3), is returning ({model_status_result}).")

    def test_instance_4(self): # feasible - first aisle only case
        instance = [3, 3, 2, 1, 1, {1:[1,2,3], 2:[4,5,6], 3:[1,3,5]}]

        model_status_result, distance_result, time_result, assignment_result = Strict_S_Shape(instance[0],
                                                                                              instance[1],
                                                                                              instance[2],
                                                                                              instance[3],
                                                                                              instance[4],
                                                                                              instance[5])
        
        self.assertEqual(model_status_result, 2, msg= f"Model status is incorrect. It should be feasible (2), is returning ({model_status_result}).")

        self.assertEqual(distance_result, 6*instance[3] + 6*(instance[4]*(instance[1] + 1)), msg = f"model is obtaining the wrong final distance. Minimum distance is {6*instance[3] + 6*(instance[4]*(instance[1] + 1))}. The model is achieving {distance_result}.")

if __name__ == "__main__":
    unittest.main()