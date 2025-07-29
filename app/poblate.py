from app.database import SessionLocal, engine, Base
from app.models.department import Department
from app.models.subDepartment import SubDepartment
from app.models.user import User
from app.models.userSubAreaPermission import UserSubAreaPermission, PermissionLevelEnum
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crear tablas
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ---------------- Departamentos ----------------
departments = [
    Department(Name="Ingenieria"),
    Department(Name="Produccion"),
    Department(Name="Administracion")
]
db.add_all(departments)
db.commit()

# IDs
ingenieria = db.query(Department).filter_by(Name="Ingenieria").first()
produccion = db.query(Department).filter_by(Name="Produccion").first()

# ---------------- SubDepartamentos ----------------
subdepartments = [
    SubDepartment(Name="Firmar Planos", DepartmentId=ingenieria.Id),
    SubDepartment(Name="Editar Planos", DepartmentId=ingenieria.Id),
    SubDepartment(Name="Leer Planos", DepartmentId=ingenieria.Id),
    SubDepartment(Name="Leer Planos", DepartmentId=produccion.Id),
]
db.add_all(subdepartments)
db.commit()

# Buscar subareas específicas
firmar_planos = db.query(SubDepartment).filter_by(Name="Firmar Planos", DepartmentId=ingenieria.Id).first()
editar_planos = db.query(SubDepartment).filter_by(Name="Editar Planos", DepartmentId=ingenieria.Id).first()
leer_planos_produccion = db.query(SubDepartment).filter_by(Name="Leer Planos", DepartmentId=produccion.Id).first()

# ---------------- Usuarios ----------------
hashed_pw = pwd_context.hash("123456")
users = [
    User(UserName="athiago", Email="athiago@espel.com.ar",
         DepartmentId=ingenieria.Id, IsActive=True, IsSuperuser=True,
         HashedPassword=hashed_pw),
    User(UserName="smartin", Email="smartin@espel.com.ar",
         DepartmentId=ingenieria.Id, IsActive=True, IsSuperuser=True,
         HashedPassword=hashed_pw),
    User(UserName="mmartin", Email="mmartin@espel.com.ar",
         DepartmentId=produccion.Id, IsActive=True, IsSuperuser=False,
         HashedPassword=hashed_pw),
]
db.add_all(users)
db.commit()

# Obtener usuarios
athiago = db.query(User).filter_by(UserName="athiago").first()
smartin = db.query(User).filter_by(UserName="smartin").first()
mmartin = db.query(User).filter_by(UserName="mmartin").first()

# ---------------- Permisos por subarea ----------------
# athiago: Editar Planos (Write)
db.add(UserSubAreaPermission(UserId=athiago.Id,
                              SubDepartmentId=editar_planos.Id,
                              PermissionLevel=PermissionLevelEnum.Write))

# smartin: Firmar Planos (Write)
db.add(UserSubAreaPermission(UserId=smartin.Id,
                              SubDepartmentId=firmar_planos.Id,
                              PermissionLevel=PermissionLevelEnum.Write))

# mmartin: Leer Planos en Producción (Read)
db.add(UserSubAreaPermission(UserId=mmartin.Id,
                              SubDepartmentId=leer_planos_produccion.Id,
                              PermissionLevel=PermissionLevelEnum.Read))

db.commit()

print("Datos de prueba insertados correctamente.")
db.close()
