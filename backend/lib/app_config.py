from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List

class AppConfig(BaseModel):
    """
    Represents the configuration for an application.

    This class uses Pydantic for data validation and serialization.

    Attributes:
        name (str): The name of the application. This field is required.
        description (str): A description of the application. Default is an empty string.
            Maximum length is 500 characters.
        allowed_models (List[str]): A list of allowed model names. Default is an empty list.
        default_model (str): The name of the default model to use. Default is an empty string.
        retriever (str): The name of the retriever to use. Default is "default_retriever".

    Config:
        extra (str): Set to 'ignore' to ignore any extra fields during model creation.

    Raises:
        ValueError: If the default_model is not in the list of allowed_models.

    Example:
        >>> config = AppConfig(name="MyApp", allowed_models=["model1", "model2"], default_model="model1")
        >>> config.name
        'MyApp'
    """
    name: str
    description: str = Field(default="", max_length=500)
    allowed_models: List[str] = Field(default_factory=list)
    default_model: str = ""
    retriever: str = "default_retriever"

    model_config = ConfigDict(extra='ignore')

    @model_validator(mode='after')
    def check_default_model(self) -> 'AppConfig':
        """
        Validates that the default_model is in the list of allowed_models.

        This method is automatically called after the model is created.

        Returns:
            AppConfig: The validated AppConfig instance.

        Raises:
            ValueError: If the default_model is not in the list of allowed_models.
        """
        if self.default_model and self.default_model not in self.allowed_models:
            raise ValueError('default_model must be in allowed_models')
        return self