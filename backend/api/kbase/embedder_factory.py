from backend.api.kbase.base_embedder_gateway import BaseEmbedderGateway
from backend.api.kbase.embedders.boto3_embedder import Boto3EmbedderGateway
from backend.api.kbase.embedders.openai_embedder import OpenAIEmbedderGateway

def get_embedder(provider: str, **kwargs) -> BaseEmbedderGateway:
    """
    Factory function to create an embedder gateway instance.
    
    Args:
        provider (str): Either 'boto3' or 'openai'.
        **kwargs: Additional configuration parameters.

    Returns:
        An instance of BaseEmbedderGateway.
    
    Raises:
        ValueError: If the provider is unsupported or required parameters are missing.
    """
    provider = provider.lower()
    if provider == "boto3":
        region_name = kwargs.get("region_name")
        model_id = kwargs.get("model_id", "amazon.titan-embed-text-v2:0")
        if not region_name:
            raise ValueError("`region_name` is required for the boto3 embedder.")
        return Boto3EmbedderGateway(region_name=region_name, model_id=model_id)
    elif provider == "openai":
        api_key = kwargs.get("api_key")
        model = kwargs.get("model", "text-embedding-3-large")
        if not api_key:
            raise ValueError("`api_key` is required for the OpenAI embedder.")
        return OpenAIEmbedderGateway(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unsupported embedder provider: {provider}")
