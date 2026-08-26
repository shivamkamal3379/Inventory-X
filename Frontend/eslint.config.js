import js from '@eslint/js';
import globals from 'globals';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import { defineConfig, globalIgnores } from 'eslint/config';

export default defineConfig([
  globalIgnores(['dist', 'node_modules']),

  // Build/config files run in Node, not the browser.
  {
    files: ['*.config.js', 'vite.config.js', 'eslint.config.js'],
    languageOptions: {
      globals: globals.node,
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
  },

  {
    files: ['src/**/*.{js,jsx}'],
    extends: [js.configs.recommended, reactHooks.configs.flat.recommended],
    plugins: { react, 'react-refresh': reactRefresh },
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    settings: { react: { version: 'detect' } },
    rules: {
      // Without these two, an identifier used only inside JSX (<Icon />,
      // <motion.div />) is reported as unused. They make JSX count as usage,
      // which is the correct fix — widening varsIgnorePattern would just hide
      // genuinely dead imports as well.
      'react/jsx-uses-vars': 'error',
      'react/jsx-uses-react': 'error',

      'no-unused-vars': [
        'error',
        {
          varsIgnorePattern: '^_',
          argsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],

      'react-refresh/only-export-components': [
        'warn',
        {
          allowConstantExport: true,
          // Context hooks live beside their provider on purpose; splitting them
          // into another file to satisfy fast refresh would scatter the API.
          allowExportNames: ['useTheme', 'useToast'],
        },
      ],
    },
  },
]);
