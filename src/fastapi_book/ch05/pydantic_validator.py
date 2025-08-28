from pydantic import BaseModel, ValidationError, field_validator, model_validator
from pydantic_core import PydanticCustomError


# Correct way to inherit from PydanticCustomError
class AddressError(PydanticCustomError):
    """Custom exception for invalid address format."""

    # We need to override __new__ because PydanticCustomError uses it for instantiation
    def __new__(cls):
        # We create the instance of the parent class with our custom error details
        return super().__new__(
            cls,
            "address.error",  # The error code
            "Address is not valid, must contain street, city, country, postal_code",  # The message
        )


# reusable validator
def strip_whitespace(v: str) -> str:
    return v.strip()


class Person(BaseModel):
    username: str
    password: str
    address: str

    # Validator 1: Runs first for the 'username' field
    @field_validator("username")
    def username_must_be_alphanumeric(cls, v):
        print("1. Running username validator...")
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

    # Validator 2: Runs second for the 'password' field
    @field_validator("password")
    def password_strength(cls, v):
        print("2. Running password validator...")
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if v.isdigit() or v.isalpha():
            raise ValueError("Password must contain both letters and numbers")
        return v

    # Validator 3: Runs third for the 'address' field
    @field_validator("address")
    def address_valid(cls, v):
        print("3. Running address validator...")
        parts = v.split(",")
        if len(parts) != 4:
            raise AddressError()
        street, city, country, postal_code = [part.strip() for part in parts]
        if not all([street, city, country, postal_code]):
            raise AddressError()
        return v

    # Validator 4: Runs LAST, after all field validators are done
    @model_validator(mode='after')
    def check_password_not_in_username(self):
        print("4. Running model validator...")
        if self.username in self.password:
            raise ValueError("Password cannot contain the username")
        return self


class Post(BaseModel):
    title: str
    content: str

    _strip_fields = field_validator("title", "content")(strip_whitespace)


if __name__ == "__main__":
    try:
        person = Person(
            username="johndoe",
            password="password_for_johndoe",  # Invalid to trigger model validator
            address="123 Main St, Springfield, USA, 12345",
        )
        print("\nValidation successful!")
        print(person)
    except ValidationError as e:
        print("\nValidation Error:")
        # .errors() gives a list of dicts with detailed error info
        print(e.errors(include_url=False))
        print("-----------------")

    print("\n--- Triggering address error ---")
    try:
        Person(
            username="jane_doe",
            password="validpassword123",
            address="Invalid Address",  # This will fail first
        )
    except ValidationError as e:
        print("\nValidation Error:")
        print(e.errors(include_url=False))
        print("-----------------")

    print("\n--- Testing Post model with whitespace stripping ---")
    post_data = {
        "title": "  My Post Title  ",
        "content": "  Some interesting content.  "
    }
    post = Post(**post_data)
    print(post)
    assert post.title == "My Post Title"
    assert post.content == "Some interesting content."
