from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr


class Header(BaseModel):
    """Represents the header section of a user profile.

    Attributes:
        name (str): Full name of the user (max 120 characters).
        title (str): Professional title or designation (max 160 characters).
    """
    name: str = Field("", max_length=120)
    title: str = Field("", max_length=160)


class Contact(BaseModel):
    """Stores contact information for a user profile.

    Attributes:
        email (Optional[EmailStr]): Email address.
        phone (Optional[str]): Phone number (max 40 characters).
        website (Optional[HttpUrl]): Personal or professional website.
        github (Optional[str]): GitHub profile link.
        linkedin (Optional[str]): LinkedIn profile link.
        location (Optional[str]): Physical location (max 120 characters).
    """
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=40)
    website: Optional[HttpUrl] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = Field(None, max_length=120)


class Project(BaseModel):
    """Defines a project entry in a user profile.

    Attributes:
        title (str): Name of the project (max 140 characters).
        desc (str): Description of the project (max 600 characters).
        url (Optional[str]): URL link to the project.
    """
    title: str = Field(..., max_length=140)
    desc: str = Field("", max_length=600)
    url: Optional[str] = None


class Education(BaseModel):
    """Represents an education entry in a user profile.

    Attributes:
        title (str): Degree or course name.
        school (str): Name of the educational institution.
        start (str): Start date.
        end (str): End date.
        details (str): Additional details about the education.
        url (Optional[str]): URL to the institution or course.
    """
    title: str = ""
    school: str = ""
    start: str = ""
    end: str = ""
    details: str = ""
    url: Optional[str] = None


class Profile(BaseModel):
    """Encapsulates the complete user profile.

    Attributes:
        header (Header): Header section of the profile.
        contact (Contact): Contact information.
        summary (List[str]): Summary statements or objectives.
        skills (List[str]): List of technical or soft skills.
        languages (List[str]): Languages known.
        projects (List[Project]): List of projects.
        education (List[Education]): Educational background.
        avatar (Optional[str]): URL or path to the user's avatar image.
    """
    header: Header = Header()
    contact: Contact = Contact()
    summary: List[str] = []
    skills: List[str] = []
    languages: List[str] = []
    projects: List[Project] = []
    education: List[Education] = []
    avatar: Optional[str] = None
