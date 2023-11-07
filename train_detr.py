from ultralytics import RTDETR

model = RTDETR("pt/rtdetr/'rtdetr-l.pt")

if __name__ == '__main__':
    model.train(data="datasets/signboard/data.yaml",
                epochs=10000,
                batch=8,
                workers = 16,
                patience = 9999,
                device= '0',
                name='signboard')