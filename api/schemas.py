from pydantic import BaseModel

class SchemaLivro(BaseModel):
    """
    Define a estrutura de como um objeto da classe livro deve ser representado na API.
    """
    id: int
    titulo: str
    preco: float
    avaliacao: str
    disponibilidade: str
    url_imagem: str
       
    class Config:
        from_attributes = True
