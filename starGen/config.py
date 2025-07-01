def load_config(config_file):
    config = {}
    with open(config_file) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                config[key.strip()] = val.strip()
    return config
