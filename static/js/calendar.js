const calendar = document.querySelector("#calendar tbody");
const monthYear = document.getElementById("monthYear");
const prevBtn = document.getElementById("prevMonth");
const nextBtn = document.getElementById("nextMonth");
const detalhesDiv = document.getElementById("detalhesConsulta");
const titleDia = document.getElementById("selectedDateTitle");

let hoje = new Date();
let anoAtual = hoje.getFullYear();
let mesAtual = hoje.getMonth();

function gerarCalendario(ano, mes) {
  const primeiroDia = new Date(ano, mes, 1);
  const ultimoDia = new Date(ano, mes + 1, 0);

  monthYear.textContent = primeiroDia.toLocaleDateString('pt-BR', {
    month: 'long',
    year: 'numeric'
  });

  calendar.innerHTML = "";

  let diaSemana = primeiroDia.getDay();
  let linha = document.createElement("tr");

  for (let i = 0; i < diaSemana; i++) {
    linha.appendChild(document.createElement("td"));
  }

  for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
    if (linha.children.length === 7) {
      calendar.appendChild(linha);
      linha = document.createElement("tr");
    }

    const dataStr = `${ano}-${String(mes + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
    const celula = document.createElement("td");
    celula.textContent = dia;

    const temAgendamento = agendamentos.some(a => a.data === dataStr);
    if (temAgendamento) celula.classList.add("has-agendamento");

    const hojeStr = new Date().toISOString().split("T")[0];
    if (dataStr === hojeStr) celula.classList.add("today");

    celula.onclick = () => mostrarAgendamentos(dataStr);
    linha.appendChild(celula);
  }

  calendar.appendChild(linha);
}

function mostrarAgendamentos(data) {
  const encontrados = agendamentos.filter(a => a.data === data);
  titleDia.textContent = new Date(data).toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });

  if (encontrados.length === 0) {
    detalhesDiv.innerHTML = "<p>Nenhuma consulta nesta data.</p>";
  } else {
    detalhesDiv.innerHTML = encontrados.map(a => `
      <div style="margin-bottom: 10px;">
        <strong>${a.especialidade}</strong><br/>
        ${a.descricao || "Consulta padrão"}<br/>
        <span>${a.hora}</span>
      </div>
    `).join("");
  }
}

prevBtn.onclick = () => {
  mesAtual--;
  if (mesAtual < 0) {
    mesAtual = 11;
    anoAtual--;
  }
  gerarCalendario(anoAtual, mesAtual);
};

nextBtn.onclick = () => {
  mesAtual++;
  if (mesAtual > 11) {
    mesAtual = 0;
    anoAtual++;
  }
  gerarCalendario(anoAtual, mesAtual);
};

gerarCalendario(anoAtual, mesAtual);