from setuptools import setup

setup(
    name='ia-assistant-plugin',
    version='0.1.0',
    description='Asistente Inteligente para Open edX - UAGRM',
    packages=[
        'ia_assistant',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'ia_assistant = ia_assistant.ia_assistant:IAAssistantXBlock',
        ]
    }
)