---
ID: 0001
TITLE: Fix npm ERESOLVE error
STAGE: general
DATE_ISO: 2026-01-24
SURFACE: agent
MODEL: gemini
FEATURE: none
BRANCH: main
USER: user
COMMAND: ""
LABELS: ["npm", "eresolve", "react", "dependency-resolution"]
LINKS:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
FILES_YAML:
  - D:/Hacathan_2/mobile/package.json
TESTS_YAML: []
PROMPT_TEXT: |
  While running ease , I facing error in the logs Running "npm ci --include=dev" in /home/expo/workingdir/build/mobile directory
  npm error code ERESOLVE
  npm error ERESOLVE could not resolve
  npm error
  npm error While resolving: react-dom@19.2.3
  npm error Found: react@19.1.0
  npm error node_modules/react
  npm error   react@"19.1.0" from the root project
  npm error   peerOptional react@"*" from @expo/devtools@0.1.8
  npm error   node_modules/@expo/devtools
  npm error     @expo/devtools@"0.1.8" from expo@54.0.32
  npm error     node_modules/expo
  npm error       expo@"~54.0.32" from the root project
  npm error       16 more (expo-application, expo-clipboard, expo-constants, ...)
  npm error   63 more (@radix-ui/react-compose-refs, ...)
  npm error
  npm error Could not resolve dependency:
  npm error peer react@"^19.2.3" from react-dom@19.2.3
  npm error node_modules/react-dom
  npm error   peerOptional react-dom@"*" from expo-router@6.0.22
  npm error   node_modules/expo-router
  npm error     expo-router@"~6.0.22" from the root project
  npm error     1 more (@expo/cli)
  npm error   peerOptional react-dom@"*" from @expo/metro-runtime@6.1.2
  npm error   node_modules/expo-router/node_modules/@expo/metro-runtime
  npm error     @expo/metro-runtime@"^6.1.2" from expo-router@6.0.22
  npm error   12 more (@radix-ui/react-collection, ...)
  npm error
  npm error Conflicting peer dependency: react@19.2.3
  npm error node_modules/react
  npm error   peer react@"^19.2.3" from react-dom@19.2.3
  npm error   node_modules/react-dom
  npm error     peerOptional react-dom@"*" from expo-router@6.0.22
  npm error     node_modules/expo-router
  npm error       expo-router@"~6.0.22" from the root project
  npm error       1 more (@expo/cli)
  npm error     peerOptional react-dom@"*" from @expo/metro-runtime@6.1.2
  npm error   node_modules/expo-router/node_modules/@expo/metro-runtime
  npm error       @expo/metro-runtime@"^6.1.2" from expo-router@6.0.22
  npm error     12 more (@radix-ui/react-collection, ...)
  npm error
  npm error Fix the upstream dependency conflict, or retry
  npm error this command with --force or --legacy-peer-deps
  npm error to accept an incorrect (and potentially broken) dependency resolution.
  npm error
  npm error
  npm error For a full report see:
  npm error /home/expo/.npm/_logs/2026-01-24T18_26_51_406Z-eresolve-report.txt
  npm error A complete log of this run can be found in: /home/expo/.npm/_logs/2026-01-24T18_26_51_406Z-debug-0.log
RESPONSE_TEXT: |
  The `npm install` command completed successfully after updating `react` and `@types/react` to `19.2.3` in `D:/Hacathan_2/mobile/package.json`. The dependency conflict has been resolved.
---
