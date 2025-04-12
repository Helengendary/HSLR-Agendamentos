create database hslr;
use hslr;

create table Papel (
	ID_papel int auto_increment not null,
    primary key (ID_papel),
    Nome varchar(100) not null
);

create table Usuário (
	ID_usuario int auto_increment not null,
    primary key (ID_usuario),
    CPF varchar(50) not null unique,
	Email varchar(255) not null unique,
    Nome varchar(100) not null,
    Sobrenome varchar(200) not null,
    DataDeNascimento date not null,
    Genero varchar(50) not null,
    Telefone varchar(50) not null,
    Senha varchar (255) not null,
    Papel int not null,
    foreign key (Papel) references Papel(ID_papel)
);

create table Consulta (
	ID_consulta int auto_increment not null,
    primary key (ID_consulta),
    Tipo varchar(200) not null,
    DataConsulta date not null,
    Hora time not null,
    ID_medico int not null,
    ID_paciente int not null,
    foreign key (ID_medico) references Usuário(ID_usuario),
    foreign key (ID_paciente) references Usuário(ID_usuario)
);

create table MedicoSecretaria (
	ID_medicosecretaria int auto_increment not null,
    primary key (ID_medicosecretaria),
    ID_medico int not null,
    ID_secretaria int not null,
    foreign key (ID_medico) references Usuário(ID_usuario),
    foreign key (ID_secretaria) references Usuário(ID_usuario)
);

insert into Papel (Nome) values ('Secretária'),
('Médico'),
('Paciente');

select * from Usuário;