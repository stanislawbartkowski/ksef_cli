class KSEFCLI:

    @staticmethod
    def clean_work(nip: str)->None:
        """
        Cleans the working directory for the given NIP (tax identification number).
        
        Args:
            nip (str): The NIP for which to clean the working directory.
        """
        import os
        import shutil

        work_dir = os.path.join("work", nip)
        
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
            print(f"Cleaned working directory for NIP: {nip}")
        else:
            print(f"No working directory found for NIP: {nip}")
