import torch
import torch.nn as nn
import torch.nn.functional as F

class ConvBlock3D(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ConvBlock3D, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)

class UNet3D(nn.Module):
    def __init__(self, in_channels=4, out_channels=1, init_features=32):
        super(UNet3D, self).__init__()
        
        self.encoder1 = ConvBlock3D(in_channels, init_features)
        self.pool1 = nn.MaxPool3d(kernel_size=2, stride=2)
        
        self.encoder2 = ConvBlock3D(init_features, init_features * 2)
        self.pool2 = nn.MaxPool3d(kernel_size=2, stride=2)
        
        self.bottleneck = ConvBlock3D(init_features * 2, init_features * 4)
        
        self.upconv2 = nn.ConvTranspose3d(init_features * 4, init_features * 2, kernel_size=2, stride=2)
        self.decoder2 = ConvBlock3D(init_features * 4, init_features * 2)
        
        self.upconv1 = nn.ConvTranspose3d(init_features * 2, init_features, kernel_size=2, stride=2)
        self.decoder1 = ConvBlock3D(init_features * 2, init_features)
        
        self.final_conv = nn.Conv3d(init_features, out_channels, kernel_size=1)

    def forward(self, x):
        enc1 = self.encoder1(x)
        enc2 = self.encoder2(self.pool1(enc1))
        
        bottleneck = self.bottleneck(self.pool2(enc2))
        
        # Decoder
        dec2 = self.upconv2(bottleneck)
        dec2 = torch.cat((dec2, enc2), dim=1)
        dec2 = self.decoder2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat((dec1, enc1), dim=1)
        dec1 = self.decoder1(dec1)
        
        return torch.sigmoid(self.final_conv(dec1))

if __name__ == "__main__":
    model = UNet3D(in_channels=4, out_channels=1)
    x = torch.randn(1, 4, 64, 64, 64)
    y = model(x)
    print(f"Вхідний розмір: {x.shape}")
    print(f"Вихідний розмір: {y.shape}")
