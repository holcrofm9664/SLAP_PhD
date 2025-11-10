from dataclasses import dataclass
from typing import Callable, Any, Tuple


@dataclass
class Model_Results:
    status: int
    distance: float
    runtime: float
    assignment: dict[int, Tuple[int,int]]
    name: str


class Compare_Model_Results:
        def __init__(self, model1:Callable, model2:Callable):
            self.model1 = model1
            self.model2 = model2

        def state_distances(self):
            return f"The {self.model1.name} model achieves a distance of {self.model1.distance}. The {self.model2.name} model achieves a distance of {self.model2.distance}"

        def state_runtimes(self):
            return f"The {self.model1.name} model has a runtime of {round(self.model1.runtime, 2)} seconds. The {self.model2.name} model has a runtime of {round(self.model2.runtime, 2)} seconds"

        def calculate_which_model_gets_better_distance(self):
            if self.model1.distance < self.model2.distance:
                return f"The {self.model1.name} model has a shorter distance"
            elif self.model2.distance < self.model1.distance:
                return f"The {self.model2.name} model has a shorter distance"
            else:
                return f"the two methods achieve an equal distance"

        def calculate_which_model_is_quicker(self):
            if self.model1.runtime < self.model2.runtime:
                return f"The {self.model1.name} model has a shorter runtime"
            elif self.model2.runtime < self.model1.runtime:
                return f"The {self.model2.name} model has a shorter runtime"
            else:
                return f"the two models have an equal runtime"

        def calculate_distance_gap(self):
            if self.model1.distance == self.model2.distance:
                return "The models find solutions with the same distance"
            elif self.model1.distance < self.model2.distance:
                return f"The solution found by the {self.model2.name} model has a distance that is {round(self.model2.distance - self.model1.distance, 2)}m greater than that found by the {self.model1.name} model"
            elif self.model2.distance < self.model1.distance:
                return f"The solution found by the {self.model1.name} model has a distance that is {round(self.model1.distance - self.model2.distance, 2)}m greater than that found by the {self.model2.name} model"

        def calculate_percentage_distance_gap(self):
            if self.model1.distance < self.model2.distance:
                return f"The distance of the solution found by the {self.model2.name} model is {round(((self.model2.distance - self.model1.distance)/self.model1.distance)*100, 2)}% longer than that of the {self.model1.name} model"
            elif self.model2.distance < self.model1.distance:
                return f"The distance of the solution found by the {self.model1.name} model is {round(((self.model1.distance - self.model2.distance)/self.model2.distance)*100, 2)}% longer than that of the {self.model2.name} model"
            else:
                return f"The two models deliver solutions of the same distance"

        def calculate_time_gap(self):
            if self.model1.runtime == self.model2.runtime:
                return "The models have equal runtimes" 
            elif self.model1.runtime < self.model2.runtime:
                return f"The {self.model1.name} model has a runtime which is {round(self.model2.runtime - self.model1.runtime, 2)} seconds quicker than the {self.model2.name} model"
            else:
                return f"The {self.model2.name} model has a runtime which is {round(self.model1.runtime - self.model2.runtime, 2)} seconds quicker than the {self.model1.name} model"

        def calculate_percentage_time_gap(self):
            if self.model1.runtime < self.model2.runtime:
                return f"The {self.model2.name} model takes {round(((self.model2.runtime - self.model1.runtime)/self.model1.runtime)*100, 2)}% longer to run than the {self.model1.name} model"
            elif self.model2.runtime < self.model1.runtime:
                return f"{self.model1.name} takes {round(((self.model1.runtime - self.model2.runtime)/self.model2.runtime)*100, 2)}% longer to run than the {self.model2.name} model"
            else:
                return f"The two models have the same runtime"
            
        def distance_summary(self):
            if self.model1.distance < self.model2.distance:
                return f"The {self.model1.name} model has a distance of {self.model1.distance}, compared to a distance of {self.model2.distance} for the {self.model2.name} model. Hence, the distance achieved by the {self.model1.name} model is {self.model2.distance - self.model1.distance} units shorter, a {round(((self.model2.distance - self.model1.distance)/self.model2.distance)*100, 2)}% reduction in distance."
            elif self.model1.distance > self.model2.distance:
                return f"The {self.model1.name} model has a distance of {self.model1.distance}, compared to a distance of {self.model2.distance} for the {self.model2.name} model. Hence, the distance achieved by the {self.model2.name} model is {self.model1.distance - self.model2.distance} units shorter, a {round(((self.model1.distance - self.model2.distance)/self.model1.distance)*100, 2)}% reduction in distance."
            
        def time_summary(self):
            if self.model1.runtime < self.model2.runtime:
                return f"The {self.model1.name} model has a runtime of {round(self.model1.runtime, 2)} seconds, compared to a runtime of {round(self.model2.runtime, 2)} seconds for the {self.model2.name} model. Hence, the {self.model1.name} model is {round(self.model2.runtime - self.model1.runtime, 2)} seconds faster, a {round(((self.model2.runtime - self.model1.runtime)/self.model2.runtime)*100, 2)}% reduction in runtime."
            elif self.model1.runtime > self.model2.runtime:
                return f"The {self.model1.name} model has a runtime of {round(self.model1.runtime, 2)} seconds, compared to a runtime of {round(self.model2.runtime, 2)} seconds for the {self.model2.name} model. Hence, the {self.model2.name} model is {round(self.model1.runtime - self.model2.runtime, 2)} seconds faster, a {round(((self.model1.runtime - self.model2.runtime)/self.model1.runtime)*100, 2)}% reduction in runtime."



def compare_two_models(model1:Callable, model:Callable, **kwargs:Any) -> None:
    """
    Compares the key outputs of two models on a single instance

    Inputs:
    - model1: the first model whose performance we wish to test
    - model2: the second model whose performance we wish to test
    - instance: the instance on which the performance of both models will be tested
    
    Outputs:
    - summary: prints the key outputs of the models
    """

    name1 = model1.__name__
    name2 = model2.__name__

    status1, distance1, runtime1, assignments1 = model1(**kwargs)
    
    status2, distance2, runtime2, assignments2 = model2(**kwargs)

    model1 = Model_Results(status1, distance1, runtime1, assignments1, name1)
    model2 = Model_Results(status2, distance2, runtime2, assignments2, name2)

    comparison = Compare_Model_Results(model1, model2)

    print(comparison.distance_summary())
    print(comparison.time_summary())