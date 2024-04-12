cloud_model = {"google", "papago", "deepl", "microsoft"}


def decorate_model_name(model):
    if model in cloud_model:
        return model
    return f'<a style="color: var(--link-text-color);text-decoration: underline;text-decoration-style: dotted;" href="https://huggingface.co/{model}" target="_blank">{model}</a>'