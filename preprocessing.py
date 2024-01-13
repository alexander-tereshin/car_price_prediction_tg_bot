import pickle

import pandas as pd

from sklearn.preprocessing import PolynomialFeatures


class CarPricePredictorPreprocessor:
    def __init__(self, models_folder):
        self.na_imputer = self.load_pickle(models_folder, filename="na_imputer.pkl")
        self.normalizer = self.load_pickle(models_folder, filename="normalizer.pkl")
        self.ohe = self.load_pickle(models_folder, filename="ohe.pkl")
        self.ridge_regressor = self.load_pickle(
            models_folder, filename="ridge_regressor.pkl"
        )

    @staticmethod
    def load_pickle(folder, filename):
        contents = pickle.load(open((folder / filename), "rb"))
        return contents

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df.drop(labels=["torque"], axis=1, inplace=True)

        for i in ["mileage", "engine", "max_power"]:
            df[i] = df[i].str.extract(r"(\d+[.,\d]+)").replace("", None).astype("float")

        cat_features_list = ["name", "fuel", "seller_type", "transmission", "owner"]

        df_cat = df.loc[:, cat_features_list].fillna("")
        df_cat["Brand"] = df_cat.name.str.split(" ").apply(
            lambda x: x[0] if len(x) != 0 else ""
        )
        df_cat.drop("name", axis=1, inplace=True)

        df_cat_coded = pd.DataFrame(
            data=self.ohe.transform(df_cat), columns=self.ohe.get_feature_names_out()
        ).astype(int)

        df_real = df.drop(df.loc[:, cat_features_list], axis=1)

        df_real_no_na = pd.DataFrame(
            data=self.na_imputer.transform(df_real), columns=df_real.columns
        )

        df_real_no_na[["engine", "seats"]] = df_real_no_na[["engine", "seats"]].astype(
            "int"
        )

        poly = PolynomialFeatures(degree=3, interaction_only=False, include_bias=False)

        year_poly = pd.DataFrame(
            poly.fit_transform(df_real_no_na["year"].values.reshape(-1, 1))
        ).astype(int)
        df_real_no_na_poly = df_real_no_na.drop(labels="year", axis=1)
        df_real_no_na_poly = pd.concat(objs=[df_real_no_na_poly, year_poly], axis=1)

        df_real_no_na_poly.columns = df_real_no_na_poly.columns.astype("str")

        df_real_no_na_poly_std = pd.DataFrame(
            self.normalizer.transform(df_real_no_na_poly),
            columns=df_real_no_na_poly.columns,
        )

        df_final = pd.concat(objs=[df_real_no_na_poly_std, df_cat_coded], axis=1)

        df_final.columns = self.ridge_regressor.best_estimator_.feature_names_in_

        return df_final
