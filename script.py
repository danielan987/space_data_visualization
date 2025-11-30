# Import packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import requests
from io import BytesIO
from astroquery.cadc import Cadc
from astropy.io import fits
import warnings

#  Address warning message
warnings.simplefilter('ignore', category=UserWarning)

# Import data 
cadc = Cadc()
results = cadc.query_name('NGC-1068-BK') # Filter by target name
results = results[results['collection'] == 'JWST'] # Filter by James Webb Space Telescope data
results = results[results['dataRelease'] > '2022-10-29T00:00:00.000'] # Filter by release date
urls = cadc.get_data_urls(results) 

# Loop through each URL file to process and visualize data
for url in urls:
    file_name = url.split('/')[-1] 
    print(f'\nProcessing: {file_name}')
    try:
        response = requests.get(url)
        response.raise_for_status()  
        file_content = BytesIO(response.content)
        with fits.open(file_content, ignore_missing_end=True) as hdul:
            print('FITS File Opened Successfully.')
            if len(hdul) > 1 and hdul[1].data is not None:
                if hdul[1].data.ndim > 3:
                    print(f'Skipping {file_name}: Data has over 3 dimensions ({hdul[1].data.ndim}).')
                    continue 
                image_data = np.array(hdul[1].data)         
                print('Stored Data Shape:', image_data.shape)
                if image_data.ndim == 1:
                    print(f"Skipping {file_name}: Data has only 1 dimension.")
                    continue
                if np.all(np.isnan(image_data)) or np.all(image_data == 0):
                    print(f"Skipping {file_name}: Data contains only NaNs or zeros.")
                    continue                
                plt.figure(num=file_name)
                plt.axis('off')
                if image_data.ndim == 2:  
                    plt.imshow(image_data, cmap='gray')
                if image_data.ndim == 3:
                    fig, ax = plt.subplots()
                    ax.axis('off')
                    def update(frame):
                        ax.imshow(image_data[frame, :, :], cmap='gray', origin='lower')
                    ani = animation.FuncAnimation(fig, update, frames=image_data.shape[0], interval=200, repeat=True)
                plt.show()
            else:
                print('No image data found in extension 1.')
    except requests.exceptions.RequestException as e:
        print(f'ERROR: Failed to download {file_name}: {e}')
    except Exception as e:
        print(f'ERROR: Issue processing {file_name}: {e}')        
