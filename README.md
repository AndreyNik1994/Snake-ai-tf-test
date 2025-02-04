Project name: Snake-AI-Project
Description: Проект запускает небольшую простую игру в змейку, которая управляется обучающимся ИИ-агентом
(он должен обучаться, честно:)). Цель проекта: совершенствование личных навыков.
Installation:
Список необходимых модулей указан в requirements.txt. Модули можно установить стандартными средствами через pip.
Проект тестировался только на указанных версиях модулей на:

1. Windows 10 x64 22H2 под PyCharm Community Edition 2024.3.1.1
PyCharm 2024.3.1.1 (Community Edition)
Build #PC-243.22562.220, built on December 18, 2024
Runtime version: 21.0.5+8-b631.28 amd64 (JCEF 122.1.9)
VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o.
Toolkit: sun.awt.windows.WToolkit
Windows 10.0
GC: G1 Young Generation, G1 Concurrent GC, G1 Old Generation
Memory: 1500M
Cores: 12
Registry:
  ide.experimental.ui=true
  llm.show.ai.promotion.window.on.start=false
Ryzen 5 5600X 12-core, NVIDIA 3080 ti

2. Linux UBUNTU 24.04.1 LTS под PyCharm PyCharm 2024.3.1 (Community Edition)
Build #PC-243.22562.180, built on December 11, 2024
Runtime version: 21.0.5+8-b631.28 amd64 (JCEF 122.1.9)
VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o.
Toolkit: sun.awt.X11.XToolkit
Linux 6.8.0-51-generic
GC: G1 Young Generation, G1 Concurrent GC, G1 Old Generation
Memory: 2048M
Cores: 8
Registry:
  ide.experimental.ui=true
  i18n.locale=
  llm.show.ai.promotion.window.on.start=false
Current Desktop: ubuntu:GNOME
AMD FX 8320e, nvidia 3060 12gb

ВАЖНО - для более быстрой работы в процессе обучения ИИ-агента использовался ГПУ nvidia 3060 12gb. При отсутствии ГПУ на
платформе вероятно увеличение длительности обучения.

Проект запускается из файла main.py.

Данный проект был вдохновлён:
https://github.com/patrickloeber/snake-ai-pytorch
https://prrasad.medium.com/building-a-snake-game-using-python-and-tkinter-a-step-by-step-guide-652ea41d6dd0
