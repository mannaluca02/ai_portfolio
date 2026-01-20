# Portfolio Frontend

Modern, minimalist portfolio website built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- ✨ Modern, minimalist design with smooth animations
- 🎨 Custom color scheme (Seasalt, Taupe Gray, Tekhelet, Scarlet, Smoky Black)
- 🎭 Interactive Hero section with mouse-reactive particle animation
- 📜 Smooth scrolling and fade-in animations
- 💬 Animated chatbot widget with expand/minimize functionality
- 📱 Fully responsive design
- ⚡ Built with Next.js 14 App Router
- 🎯 TypeScript for type safety
- 🎨 Tailwind CSS for styling
- 🌊 Framer Motion for advanced animations

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── globals.css        # Global styles with Tailwind
│   ├── layout.tsx         # Root layout with Header/Footer
│   └── page.tsx           # Homepage
├── components/
│   ├── layout/            # Layout components
│   │   ├── Header.tsx
│   │   ├── Navigation.tsx
│   │   └── Footer.tsx
│   ├── home/              # Homepage components
│   │   └── Hero.tsx
│   ├── chatbot/           # Chatbot components
│   │   └── ChatbotWidget.tsx
│   └── ui/                # Reusable UI components
│       └── FadeInSection.tsx
├── lib/
│   └── hooks/             # Custom React hooks
│       └── useScrollAnimation.ts
└── public/                # Static assets
```

## Color Scheme

- **Seasalt** (#FAFAFA) - Background
- **Taupe Gray** (#8A8D93) - Secondary text
- **Tekhelet** (#3D348B) - Primary accent
- **Scarlet** (#FF3A20) - Action/hover accent
- **Smoky Black** (#090302) - Primary text

## Features Explained

### Interactive Hero Animation
The Hero section features a particle system that reacts to mouse movement, creating an engaging first impression.

### Chatbot Widget
- Appears in center of screen initially
- After 3 seconds (if not clicked), animates to bottom-right corner
- Expands into full chat interface on click
- Smooth animations using Framer Motion

### Scroll Animations
All sections use the `FadeInSection` component for smooth fade-in animations as you scroll down the page.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Next Steps

1. Connect to backend API (backend)
2. Implement full chatbot functionality
3. Add portfolio sections (Experience, Projects, Skills, etc.)
4. Add contact form
5. Optimize images and performance

## License

Private project - FHNW
