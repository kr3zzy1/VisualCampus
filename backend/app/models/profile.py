from typing import Literal
from pydantic import BaseModel,Field
Category=Literal['campus','dormitory','classroom','library','city','sports','laboratories','student_life']
class University(BaseModel):name:str;country:str|None=None;region:str|None=None;website:str|None=None;domain:str|None=None
class Photo(BaseModel):id:str;thumbnail_url:str;source_url:str;title:str;category:Category;confidence:int=Field(ge=0,le=100);status:Literal['verified','partial'];reasons:list[str]
class WebSource(BaseModel):title:str;url:str
class Profile(BaseModel):university:University;summary:str;categories:dict[Category,list[Photo]];web_sources:list[WebSource]=[];warnings:list[str]=[]
class SearchRequest(BaseModel):query:str=Field(min_length=2,max_length=160)
class Job(BaseModel):id:str;status:Literal['processing','completed','failed','ambiguous'];progress:list[str]=[];candidates:list[University]=[];profile:Profile|None=None;error:str|None=None
