create database hslr;
drop database hslr;
use hslr;

create table Papel (
	ID_papel int auto_increment not null,
    primary key (ID_papel),
    Nome varchar(100) not null
);

create table Usuario (
	ID_usuario int auto_increment not null,
    primary key (ID_usuario),
    CPF varchar(50) not null unique,
	Email varchar(255) not null unique,
    Nome varchar(100) not null,
    Sobrenome varchar(200) not null,
    DataDeNascimento date not null,
    Telefone varchar(50) not null,
    Senha varchar (255) not null,
    Imagem mediumblob DEFAULT NULL,
    Papel int not null,
    foreign key (Papel) references Papel(ID_papel)
);

create table MedicoSecretaria (
	ID_medicosecretaria int auto_increment not null,
    primary key (ID_medicosecretaria),
    ID_medico int not null,
    ID_secretaria int not null,
    foreign key (ID_medico) references Usuario(ID_usuario),
    foreign key (ID_secretaria) references Usuario(ID_usuario)
);

create table CategoriaExame (
	ID_categoriaExame int auto_increment not null,
    primary key (ID_categoriaExame),
    Nome varchar(100) unique
);

create table Exame(
	ID_exame int auto_increment not null,
    primary key (ID_exame),
    Nome varchar (100),
    Descricao varchar(500),
    Imagem mediumblob DEFAULT NULL,
    ID_categoria int not null,
    foreign key (ID_categoria) references CategoriaExame(ID_categoriaExame)
);

create table Consulta (
	ID_consulta int auto_increment not null,
    primary key (ID_consulta),
    ID_Exame int not null,
    DataConsulta date not null,
    Hora time not null,
    ID_medico int not null,
    ID_paciente int not null,
    foreign key (ID_medico) references Usuario(ID_usuario),
    foreign key (ID_paciente) references Usuario(ID_usuario),
    foreign key (ID_Exame) references Exame(ID_exame)
);

insert into Papel (Nome) values ('Secretária'),
('Médico'),
('Paciente');

insert into CategoriaExame (Nome) values ('Hormonal'), 
('Obstétrico'),
('Imagem'),
('Preventivo'),
('Menopausa'),
('Laboratorial'),
('Fertilidade');

insert into Exame (Nome, Descricao, Imagem, ID_categoria) values
('Papanicolau', 'Coleta de células do colo do útero.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/utero_img.webp'), 4),
('Colposcopia', 'Avaliação com aparelho óptico.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Colposcopia_img.jpg'), 4),
('Ultrassonografia Obstétrica', 'Avaliação da gestação.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/ultrassom_obstétrico_img.jpg'), 2),
('Ultrassonografia Transvaginal', 'Avaliação interna do útero.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/ultrassom-transvaginal_img.webp'), 3),
('Mamografia', 'Exame das mamas.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/mamografia_img.jpg'), 3),
('Beta hCG', 'Confirmação de gravidez.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/beta_img.webp'), 6),
('Densitometria Óssea', 'Avaliação óssea.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/densiometria_img.webp'), 5),
('Ultrassonografia das Mamas', 'Dosagem de hormônios.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/ultrassom_mamas_img.png'), 3),
('Perfil Hormonal', 'Dosagem de hormônios.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/exame_hormonal_img.jpg'), 1),
('Doppler Fetal', 'Avaliação do fluxo sanguíneo fetal.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/doppler_fetal.webp'), 2),
('Teste de Streptococcus B', 'Detecção de infecção bacteriana.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/streptococcus-b.webp'), 2),
('Teste de HPV', 'Identificação do vírus HPV.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/teste_hpv.jpg'), 4),
('Glicemia e Colesterol', 'Avaliação metabólica geral.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/glicemia_colesterol.jpg'), 6),
('Exame de Fertilidade', 'Avaliação hormonal e ovariana.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/fertilidade_img.webp'), 7),
('Dosagem de Hormônios', 'Avaliação hormonal geral.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/exame_hormonal_img.jpg'), 1),
('Exame de Mioma', 'Avaliação de miomas uterinos.', LOAD_FILE('C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/miomas_img.jpg'), 3);


select * from Papel;
select E.Nome as Nome, E.Descricao as Descricao, E.Imagem as Imagem, C.Nome as 'Categoria' from Exame E inner join CategoriaExame C on C.ID_categoriaExame = E.ID_categoria;
select E.Nome as Nome, E.Descricao as Descricao, E.Imagem as Imagem, C.Nome as 'Categoria' from Exame E inner join CategoriaExame C on C.ID_categoriaExame = E.ID_categoria where C.Nome = 'Hormonal';