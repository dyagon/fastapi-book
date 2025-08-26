from pydantic import (
    BaseModel,
    DirectoryPath,
    IPvAnyAddress,
    FilePath,
    EmailStr,
    NameEmail,
    SecretStr,
    SecretBytes,
    HttpUrl,
    Json,
    ValidationError
)
from datetime import date, datetime

from typing import Optional


class ComplexPerson(BaseModel):
    name: str
    age: int
    age2: Optional[int] = None
    enable: bool
    hobbies: list[str]
    address: dict[str, str]
    birthday: date

    # complex types
    filePath: FilePath
    dirPath: DirectoryPath
    ip: IPvAnyAddress
    email: EmailStr
    nameEmail: NameEmail
    secretStr: SecretStr
    secretBytes: SecretBytes
    website: HttpUrl
    json_obj: Json


class Person(BaseModel):
    name: str
    nums: str = ""
    age: Optional[int] = None


if __name__ == "__main__":
    person = Person(name="John")
    print(person)
    print(person.model_dump())
    print(person.model_dump_json())

    new_person = person.model_copy(update={"age": 30})
    print(new_person)


    try:
        person = Person()
    except ValidationError as e:
        print("Validation Error:")
        print("-------------")
        print(e.errors())
        print("-------------")
        print(e.json())
        print("-------------")
        print(str(e))
        print("-------------")
    else:
        print(person)

