PhiBulkShearDecomp.py was built to read in dilution factors of bulk and shear in the coating along with data files containing mode frequencies (column 1), loss angle (column 2), and standard deviation (column 3).

Data files should be space delineated.

IMPORTANT:
The data I included was from AlGaAs coated Silicon samples at cold temperatures. The code does NOT properly fit this data, as it displays some whack behavior. I recommend finding some nice amorphous room temperature coating data to test out this program and see if it will work for you. I only included my data here for completeness so anyone can replicate my work.

For an explanation of how the code works, there are comments inside the code. The big picture of how it works can be read in https://journals.aps.org/prd/pdf/10.1103/PhysRevD.101.042004?casa_token=RF_9tHOpXi0AAAAA%3A5jKwDHs5N-RFbkoAxZ1qWbu30UaJA78qBgX7HmIa3BIAF_g6SoYLjtSkI_3DNLhSI5WYDfLnu7hR

Or search in google scholar "Vajente Method for the Experimental Measurement of Bulk and Shear Loss Angles in Amorphous Thin Films"