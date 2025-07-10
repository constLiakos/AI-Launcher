// src/main/utils/config.ts
import { app } from 'electron';
import { join } from 'path';

export const isDev = !app.isPackaged;

export const getAppDataPath = (): string => {
  return app.getPath('userData');
};

export const getDatabasePath = (): string => {
  return join(getAppDataPath(), 'conversations.db');
};

export const getAssetsPath = (): string => {
  let path;
  if (isDev) {
    path = join(process.cwd(), 'assets');
  }
  else{
    path = join(process.resourcesPath, 'assets');
  }
  console.log("Assets path: ", path);
  return path;
}
