from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer

app = FastAPI()
app.title = 'Mi app con FastAPI'


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request): 
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != 'admin@gmail.com':
            raise HTTPException(status_code=403, detail='Credenciales invalidas')


class User(BaseModel):
    email: str
    password: str


class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=3, max_length=15)
    overview: str = Field(default='Descripcion de la película', min_length=15, max_length=50)
    year: int = Field(default=2022, le=2022)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=3, max_length=15)


movies = [
    {
        'id': 1,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2009',
        'rating': 7.8,
        'category': 'Acción'    
    },

    {
        'id': 2,
        'title': 'Duro de Matar',
        'overview': "Persona que se considera díficil de asesinar",
        'year': '2009',
        'rating': 7.8,
        'category': 'Acción'    
    },

    {
        "id": 3,
        "title": "Paul",
        "overview": "El extraterrestre buena onda",
        "year": 0,
        "rating": 8.5,
        "category": "Comedia"
    }
]

@app.get('/', tags=['home'])
def message():
    return HTMLResponse('<h1>Hello</h1>')


@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == 'admin@gmail.com' and user.password == 'admin':
        token: str = create_token(user.dict())
    return token 


@app.get('/movies', tags=['movies'], response_model=List[Movie], dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]: # -> tipoParametro: indica que tiene que devolver la funcion 
    return JSONResponse(content=movies)


@app.get('/movies/{id}', tags=['movies'])
def get_movie(id: int = Path(ge=1, le=2000)):
    movie = list(filter(lambda x: x['id'] == id,movies))
    return JSONResponse(content=movie[0]) or "No se encontro la pelicula"

 
@app.get('/movies/', tags=['movies'], response_model=List[Movie])
def get_movies_by_category(category: str = Query(min_length=3, max_length=15)) -> List[Movie]: #Query: cuando el parametro recibe la funcion y no la ruta
    if category == movies.category: 
        list_movies = list(filter(lambda x: x['category'] == category,movies))
        movies_category = [movie for movie in list_movies]
        return JSONResponse(content=movies_category)
        #Otra opcion
        #return [ item for item in movies if item['category'] == category]

#Opcional pero no recomendado
'''@app.post('/movies', tags=['movies'])
def create_movie(id: int = Body(), 
                 title: str = Body(), 
                 overview: str = Body(), 
                 year: int = Body(), 
                 rating: float = Body(), 
                 category: str = Body()):
    #se importa Body de fastapi y se asigna a cada parametro 
    #De esa forma se considera como un objeto
    movies.append({
        'id': id,
        'title': title,
        'overview': overview,
        'year': year,
        'rating': rating,
        'category': category
    })
    
    return movies'''


@app.post('/movies', tags=['movies'], response_model=dict)
def create_movie(movie: Movie) -> dict:
    movies.append(movie)
    return JSONResponse(content={'message': 'Se ha registrado la película'})


@app.put('/movies/{id}', tags=['movies'], response_model=dict)
def update_movie(id: int, movie: Movie) -> dict:
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['rating'] = movie.rating
            item['category'] = movie.category

            return JSONResponse(content={'message': 'Se ha modificado la película'})


@app.delete('/movies/{id}', tags=['movies'], response_model=dict)
def delete_movie(id: int) -> dict:
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
            return JSONResponse(content={'message': 'Se ha eliminado la película'})
