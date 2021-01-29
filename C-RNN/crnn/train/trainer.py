import numpy as np
import torch
from torchvision.utils import make_grid
from .base_trainer import BaseTrainer

from tqdm import tqdm

# Structure based off https://github.com/victoresque/pytorch-template
class Trainer(BaseTrainer):
    """
    Trainer class

    Note:
        Inherited from BaseTrainer.
    """
    def __init__(self, model, loss, metrics, optimizer, resume, config,
                 data_loader, valid_data_loader=None, lr_scheduler=None, train_logger=None):
        
        super(Trainer, self).__init__(model, loss, metrics, optimizer, resume, config, train_logger)

        self.data_loader = data_loader
        self.valid_data_loader = valid_data_loader
        self.do_validation = self.valid_data_loader is not None
        self.lr_scheduler = lr_scheduler
        self.log_step = int(np.sqrt(data_loader.batch_size))

    def _eval_metrics(self, output, target):
        acc_metrics = np.zeros(len(self.metrics))
        for i, metric in enumerate(self.metrics):
            acc_metrics[i] += metric(output, target)
            
            #self.writer.add_scalar("%s"%metric.__name__, acc_metrics[i])
            #self.writer.add_scalar(f'{metric.__name__}', acc_metrics[i])
        return acc_metrics

    def _train_epoch(self, epoch):
        """
        Training logic for an epoch

        :param epoch: Current training epoch.
        :return: A log that contains all information you want to save.

        Note:
            If you have additional information to record, for example:
                > additional_log = {"x": x, "y": y}
            merge it with log before return. i.e.
                > log = {**log, **additional_log}
                > return log

            The metrics in log must have the key 'metrics'.
        """
        self.model.train()
    
        total_loss = 0
        total_metrics = np.zeros(len(self.metrics))

        self.writer.set_step(epoch) 

        _trange = tqdm(self.data_loader, leave=True, desc='')

        for batch_idx, batch in enumerate(_trange):
            batch = [b.to(self.device) for b in batch]
            data, target = batch[:-1], batch[-1]
            data = data if len(data) > 1 else data[0] 
            #data, target = data.to(self.device), target.to(self.device)

            self.optimizer.zero_grad()
            output = self.model(data)

            loss = self.loss(output, target)
            loss.backward()
            self.optimizer.step()

            #self.writer.set_step((epoch - 1) * len(self.data_loader) + batch_idx)
            #self.writer.add_scalar('loss', loss.item())
            total_loss += loss.item()
            total_metrics += self._eval_metrics(output, target)


            if self.verbosity >= 2 and batch_idx % self.log_step == 0:                
                _str = 'Train Epoch: {} Loss: {:.6f}'.format(epoch,loss.item()) 
                _trange.set_description(_str)

        # Add epoch metrics
        loss = total_loss / len(self.data_loader)
        metrics = (total_metrics / len(self.data_loader)).tolist()

        self.writer.add_scalar('loss', loss)
        for i, metric in enumerate(self.metrics):
            self.writer.add_scalar("%s"%metric.__name__, metrics[i])

        

        if self.config['data']['format'] == 'image':
            self.writer.add_image('input', make_grid(data.cpu(), nrow=8, normalize=True))

        log = {
            'loss': loss,
            'metrics': metrics
        }

        if self.do_validation:
            val_log = self._valid_epoch(epoch)
            log = {**log, **val_log}

        if self.lr_scheduler is not None:
            self.lr_scheduler.step()

        return log

    def _valid_epoch(self, epoch):
        """
        Validate after training an epoch

        :return: A log that contains information about validation

        Note:
            The validation metrics in log must have the key 'val_metrics'.
        """
        self.model.eval()
        total_val_loss = 0
        total_val_metrics = np.zeros(len(self.metrics))


        self.writer.set_step(epoch, 'valid')        

        with torch.no_grad():

            for batch_idx, batch in enumerate(self.valid_data_loader):
                batch = [b.to(self.device) for b in batch]
                data, target = batch[:-1], batch[-1]
                data = data if len(data) > 1 else data[0] 
            
                output = self.model(data)
                loss = self.loss(output, target)

                # self.writer.set_step((epoch - 1) * len(self.valid_data_loader) + batch_idx, 'valid')
                # self.writer.add_scalar('loss', loss.item())

                total_val_loss += loss.item()
                total_val_metrics += self._eval_metrics(output, target)

                #self.writer.add_image('input', make_grid(data.cpu(), nrow=8, normalize=True))


            # Add epoch metrics
            val_loss = total_val_loss / len(self.valid_data_loader)
            val_metrics = (total_val_metrics / len(self.valid_data_loader)).tolist()

            # DELETE THIS SHIT
            ret = 0
            
            self.writer.add_scalar('loss', val_loss)
            for i, metric in enumerate(self.metrics):
                self.writer.add_scalar("%s"%metric.__name__, val_metrics[i])
            
                # DELETE THIS SHIT
                if metric.__name__ == 'val_accuracy': ret = val_metrics[i]

            if self.config['data']['format'] == 'image':
                self.writer.add_image('input', make_grid(data.cpu(), nrow=8, normalize=True))

    
            #for name, param in self.model.named_parameters():
            #    if param.requires_grad:
            #        self.writer.add_histogram(name, param.clone().cpu().numpy(), bins='doane')


        return {
            'val_loss': val_loss,
            'val_metrics':val_metrics
            }
