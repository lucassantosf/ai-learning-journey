frontend/
├── public/                # Arquivos estáticos (favicon, manifest, etc)
│   └── vite.svg
├── src/
│   ├── assets/            # Imagens, ícones, fontes...
│   ├── components/        # Componentes reutilizáveis (Button, Header, etc)
│   ├── context/           # Contextos globais (AuthContext, etc)
│   ├── pages/             # Páginas da aplicação (Home, Dashboard...)
│   │   └── Home/
│   │       ├── Home.tsx
│   │       └── index.ts
│   ├── routes/            # Configuração das rotas (React Router)
│   │   └── index.tsx
│   ├── services/          # Requisições à API (fetch/axios)
│   ├── App.tsx            # Componente raiz
│   ├── index.css          # Estilos globais
│   └── main.tsx           # Ponto de entrada
├── .gitignore             # Arquivos e pastas ignorados pelo git
├── Dockerfile             # Configurações de build do Docker
├── eslint.config.js       # Configurações do ESLint
├── index.html             # Página HTML principal
├── nginx.conf             # Configurações do Nginx
├── package-lock.json      # Bloqueio de versões de dependências
├── package.json           # Dependências e scripts do projeto
├── README.md              # Documentação do projeto
├── tsconfig.app.json      # Configurações TypeScript para o aplicativo
├── tsconfig.json          # Configurações principais do TypeScript
├── tsconfig.node.json     # Configurações TypeScript para Node.js
└── vite.config.ts         # Configurações do Vite
