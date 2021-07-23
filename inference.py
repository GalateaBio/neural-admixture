import json
import logging
import sys
import torch
from model.neural_admixture import NeuralAdmixture
from src import utils

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def main():
    args = utils.parse_args(train=False)
    log.info('Using {} GPU(s)'.format(torch.cuda.device_count()) if torch.cuda.is_available() else 'No GPUs available.')
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    data_file_str = args.data_file
    out_name = args.out_name
    weights_file_str = f'{args.save_dir}/{args.name}.pt'
    config_file_str = f'{args.save_dir}/{args.name}_config.json'
    try:
        with open(config_file_str, 'r') as fb:
            config = json.load(fb)
    except FileNotFoundError as fnfe:
        log.error(f'Config file ({config_file_str}) not found. Make sure it is in the correct directory and with the correct name.')
        return 1
    except Exception as e:
        raise e
    log.info('Model config file loaded. Loading weights...')
    model = NeuralAdmixture(config['Ks'], num_features=config['num_snps'])
    model.load_state_dict(torch.load(weights_file_str, map_location=device), strict=True)
    model.to(device)
    log.info('Model weights loaded. Reading data...')
    X, _, _, _ = utils.read_data(data_file_str)
    assert X.shape[1] == config['num_snps'], 'Number of SNPs in data does not correspond to number of SNPs the network was trained on.'
    log.info('Data loaded and validated. Running inference...')
    preds = utils.get_model_predictions(model, X, bsize=args.batch_size, device=device)
    utils.write_outputs(model, X, valX=None, bsize=args.batch_size,
                        device=device, run_name=out_name,
                        out_path=args.save_dir, only_Q=True)

if __name__ == '__main__':
    sys.exit(main())