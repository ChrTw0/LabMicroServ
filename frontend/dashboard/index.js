import { AppRegistry, Platform } from 'react-native';
import App from './App'; // Importa tu componente principal
import * as app from './app.json';

// Si no hay un elemento 'root' disponible, el renderizado fallará.
const rootTag = document.getElementById('root');

// Registra la aplicación en el registro de componentes
AppRegistry.registerComponent(app.expo.name, () => App);

// Inicializa la aplicación en la plataforma web
if (Platform.OS === 'web') {
  AppRegistry.runApplication(app.expo.name, {
    initialProps: {},
    rootTag,
  });
}